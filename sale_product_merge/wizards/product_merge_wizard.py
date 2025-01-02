# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductMergeWizard(models.TransientModel):

    _inherit = "product.merge.wizard"

    def _move_variant_to_template(self, product_variant, attribute_values):
        pricelist_items = self.env["product.pricelist.item"].search(
            [
                ("applied_on", "=", "1_product"),
                ("product_tmpl_id", "=", product_variant.product_tmpl_id.id),
            ]
        )
        pricelist_items.write(
            {
                "applied_on": "0_product_variant",
                "product_id": product_variant.id,
                "product_tmpl_id": self.product_tmpl_id.id,
            }
        )
        return super()._move_variant_to_template(product_variant, attribute_values)
