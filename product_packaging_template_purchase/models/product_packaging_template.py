# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductPackagingTemplate(models.Model):
    _inherit = "product.packaging.template"

    purchase = fields.Boolean(
        default=True, help="If true, the packaging can be used for purchase orders"
    )

    def write(self, vals):
        """
        Propagate changes on packages at variant level.
        """
        res = super().write(vals)
        if "purchase" in vals:
            self.mapped("packaging_ids").write({"purchase": vals["purchase"]})
        return res

    def _prepare_create_values_for_packaging(self):
        res = super()._prepare_create_values_for_packaging()
        res["purchase"] = self.purchase
        return res
