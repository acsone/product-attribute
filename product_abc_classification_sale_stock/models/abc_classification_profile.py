# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta
from operator import attrgetter

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class AbcClassificationProfile(models.Model):

    _inherit = "abc.classification.profile"

    profile_type = fields.Selection(
        selection_add=[
            (
                "sale_stock",
                "Based on the count of delivered sale order line by product",
            )
        ]
    )
    warehouse_id = fields.Many2one(
        "stock.warehouse",
        "Warehouse",
        ondelete="cascade",
        default=lambda self: self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.user.company_id.id)], limit=1
        ),
    )

    @api.constrains("profile_type", "warehouse_id")
    def _check_warehouse_id(self):
        for rec in self:
            if rec.profile_type == "sale_stock" and not rec.warehouse_id:
                raise ValidationError(
                    _(
                        "You must specify a warehouse for {profile_name}"
                    ).forman(profile_name=rec.name)
                )

    def _fill_initial_product_data(self, date):
        product_list = []
        if self.profile_type == "sale_stock":
            return self._fill_data(date, product_list)
        return product_list, 0

    def _get_data(self, from_date=None):
        self.ensure_one()
        from_date = (
            from_date
            if from_date
            else fields.Datetime.to_string(
                datetime.today() - timedelta(days=self.period)
            )
        )
        customer_location_ids = (
            self.env["stock.location"].search([("usage", "=", "customer")]).ids
        )
        # Count the number of delivered order line by product linked to a
        # stock_move with a customer location as destination and a date later
        # than the given date
        self.env.cr.execute(
            """ SELECT
                        sol.product_id product_id,
                        COUNT(sol.id) number_of_so_lines
                    FROM
                        sale_order so
                    JOIN
                        sale_order_line sol ON
                        sol.order_id = so.id
                    JOIN
                        abc_classification_profile_product_rel rel
                        ON rel.product_id = sol.product_id
                    WHERE sol.qty_delivered > 0
                        AND rel.profile_id = %(profile_id)s
                        AND so.warehouse_id = %(current_warehouse_id)s
                    AND EXISTS (
                            SELECT
                                1
                            FROM
                                stock_move sm
                            JOIN
                                procurement_order po
                                on po.id = sm.procurement_id
                            WHERE
                                sm.date > %(start_date)s
                                AND sm.location_dest_id in %(customer_loc_ids)s
                                AND po.sale_line_id = sol.id
                        )

                    GROUP BY sol.product_id
                    ORDER BY number_of_so_lines DESC
        """,
            {
                "start_date": from_date,
                "current_warehouse_id": self.warehouse_id.id,
                "profile_id": self.id,
                "customer_loc_ids": tuple(customer_location_ids),
            },
        )

        result = self.env.cr.fetchall()
        # Get All products with the profile...
        self.env.cr.execute(
            """
            SELECT
                product_id
            FROM
                abc_classification_profile_product_rel
            WHERE
                profile_id = %(profile_id)s
        """,
            {"profile_id": self.id},
        )
        all_product_ids = {r[0] for r in self.env.cr.fetchall()}
        total = 0
        product_list = []
        for r in result:
            product_id = r[0]
            product_data = {
                "product": self.env["product.product"].browse(product_id),
                "number_of_so_lines": int(r[1]),
            }
            total += int(r[1])
            product_list.append(product_data)
            all_product_ids.remove(product_id)
        # Add all products not sold or not delivered into this timelapse
        for product_id in all_product_ids:
            product_list.append(
                {
                    "product": self.env["product.product"].browse(product_id),
                    "number_of_so_lines": 0,
                }
            )
        return product_list, total

    def _build_ordered_level_cumulative_percentage(self):
        """Return an ordered list of tuple of level, cumulative percentage

        The ordering is based on the level with the higher percentage first
        """
        self.ensure_one()
        levels = self.level_ids.sorted(
            key=attrgetter("percentage"), reverse=True
        )
        percentages = levels.mapped("percentage")
        cum_percentages = []
        previous_percentage = None
        for i, perc in enumerate(percentages):
            if i == 0:
                percentage_to_append = perc
                cum_percentages.append(percentage_to_append)
            else:
                percentage_to_append = previous_percentage + perc
                cum_percentages.append(percentage_to_append)
            previous_percentage = percentage_to_append

        return list(zip(levels, cum_percentages))

    @api.multi
    def _compute_abc_classification(self):
        to_compute = self.filtered((lambda p: p.profile_type == "sale_stock"))
        remaining = self - to_compute
        res = None
        if remaining:
            res = super(
                AbcClassificationProfile, remaining
            )._compute_abc_classification()
        ProductClassification = self.env["abc.classification.product.level"]

        for profile in to_compute:
            product_list, total = profile._get_data()
            level_percentage = (
                profile._build_ordered_level_cumulative_percentage()
            )
            level, percentage = level_percentage.pop(0)
            previous_data = {}
            for i, product_data in enumerate(product_list):

                # Compute percentages and cumulative percentages for the products
                product_data["number_of_so_lines_percentage"] = (
                    (100.0 * product_data["number_of_so_lines"] / total)
                    if total
                    else 0.0
                )

                product_data["cumulative_percentage"] = (
                    product_data["number_of_so_lines_percentage"]
                    if i == 0
                    else (
                        product_data["number_of_so_lines_percentage"]
                        + previous_data["cumulative_percentage"]
                    )
                )
                if product_data["cumulative_percentage"] > 100:
                    raise UserError(
                        _("Cumulative percentage greater than 100.")
                    )

                # Compute ABC classification for the products based on the
                # cumulative percentage

                if (
                    product_data["cumulative_percentage"] > percentage
                    and len(level_percentage) > 0
                ):
                    level, percentage = level_percentage.pop(0)

                product_abc_classification = product_data[
                    "product"
                ].abc_classification_product_level_ids.filtered(
                    lambda p, profile: p.profile_id == profile.id
                )

                if product_abc_classification:
                    product_abc_classification.write(
                        {"computed_level_id": level.id}
                    )
                else:
                    ProductClassification.create(
                        {
                            "product_id": product_data["product"].id,
                            "profile_id": profile.id,
                            "computed_level_id": level.id,
                        }
                    )

                previous_data = product_data
        return res
