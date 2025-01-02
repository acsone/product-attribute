# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, _, api, fields, models
from odoo.exceptions import ValidationError


class ProductMergeWizard(models.TransientModel):
    _name = "product.merge.wizard"
    _description = "Merge Products Wizard"

    product_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        string="Product Model",
        domain="[('id', 'in', product_ids)]",
        required=True,
    )
    product_ids = fields.Many2many(
        comodel_name="product.template", string="Products to Merge", required=True
    )
    attribute_ids = fields.Many2many(
        comodel_name="product.attribute", string="Attributes", required=True
    )
    line_ids = fields.One2many(
        comodel_name="product.merge.wizard.line",
        inverse_name="wizard_id",
        string="Attribute Mapping",
        compute="_compute_line_ids",
        store=True,
        readonly=False,
    )

    @api.constrains("product_ids")
    def _check_minimum_products(self):
        """
        Ensure that at least two products are selected for merging.
        """
        for wizard in self:
            if len(wizard.product_ids) < 2:
                raise ValidationError(
                    _(
                        "At least two products must be added to the wizard to perform a merge."
                    )
                )

    @api.constrains("product_ids")
    def _check_products_max_one_variant(self):
        for wizard in self:
            for product in wizard.product_ids:
                if len(product.product_variant_ids) > 1:
                    raise ValidationError(
                        _(
                            "All added products must have at most one variant. "
                            "Product '%(product)s' has multiple variants.",
                            product=product.name,
                        )
                    )

    @api.constrains("product_ids")
    def _check_product_types(self):
        for wizard in self:
            if len(wizard.product_ids) > 1:
                types = wizard.product_ids.mapped("type")
                if len(set(types)) > 1:
                    raise ValidationError(
                        _(
                            "All products to merge must be of the same type "
                            "(e.g., consumable, service, or storable)."
                        )
                    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get(
            "active_model"
        ) != "product.template" or not self.env.context.get("active_ids"):
            return res
        res["product_ids"] = [Command.set(self.env.context["active_ids"])]
        return res

    def action_merge_products(self):
        self.ensure_one()
        self.product_tmpl_id.with_context(product_merge=True).write(
            {
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [
                                Command.link(value.id) for value in attribute.value_ids
                            ],
                        }
                    )
                    for attribute in self.attribute_ids
                ],
            }
        )
        other_templates = (
            self.line_ids.product_id.product_tmpl_id - self.product_tmpl_id
        )
        for line in self.line_ids:
            product_variant = line.product_id
            self._update_supplier_info(product_variant)
            self._move_variant_to_template(product_variant, line.attribute_value_ids)

        other_templates.write({"active": False})
        archived_links = "<li>".join(
            f'<a href="#" data-oe-model="product.template" '
            f'data-oe-id="{template.id}">{template.name}</a></li>'
            for template in other_templates
        )
        self.product_tmpl_id.message_post(
            body=_(
                "The following products were merged and archived:"
                "<br/><ul>%(archived_links)s<ul>",
                archived_links=archived_links,
            ),
            subtype_xmlid="mail.mt_note",
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": "product.template",
            "res_id": self.product_tmpl_id.id,
            "view_mode": "form",
            "target": "current",
        }

    def _move_variant_to_template(self, product_variant, attribute_values):
        template_attribute_value = self.env["product.template.attribute.value"].search(
            [
                ("product_tmpl_id", "=", self.product_tmpl_id.id),
                ("product_attribute_value_id", "in", attribute_values.ids),
            ]
        )
        product_variant.write(
            {
                "product_tmpl_id": self.product_tmpl_id.id,
                "product_template_attribute_value_ids": [
                    Command.set(template_attribute_value.ids)
                ],
            }
        )
        product_variant._compute_combination_indices()

    @api.depends("product_ids")
    def _compute_line_ids(self):
        for rec in self:
            rec.update(
                {
                    "line_ids": [
                        Command.create({"product_id": p.id})
                        for p in rec.product_ids.product_variant_ids
                    ]
                }
            )

    def _update_supplier_info(self, product_variant):
        """
        Updates supplier information by transferring supplierinfo from the merged
        products to the target product template.
        """
        self.ensure_one()
        supplier_infos = self.env["product.supplierinfo"].search(
            [("product_tmpl_id", "=", product_variant.product_tmpl_id.id)]
        )
        supplier_infos.write({"product_id": product_variant.id})
        supplier_infos = self.env["product.supplierinfo"].search(
            [("product_id", "=", product_variant.id)]
        )
        supplier_infos.write({"product_tmpl_id": self.product_tmpl_id.id})
