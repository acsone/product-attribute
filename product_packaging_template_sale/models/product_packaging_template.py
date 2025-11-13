# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductPackagingTemplate(models.Model):
    _inherit = "product.packaging.template"

    sales = fields.Boolean(
        default=True, help="If true, the packaging can be used for sales orders"
    )

    def write(self, vals):
        """
        Propagate changes on packages at variant level.
        """
        res = super().write(vals)
        if "sales" in vals:
            self.mapped("packaging_ids").write({"sales": vals["sales"]})
        return res

    def _prepare_create_values_for_packaging(self):
        res = super()._prepare_create_values_for_packaging()
        res["sales"] = self.sales
        return res
