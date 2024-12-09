# Copyright 2020 Akretion - Mourad EL HADJ MIMOUNE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    sale_markup = fields.Float(
        string="Markup (%)",
        default=0,
        digits=(16, 2),
        help="Margin to apply on price to obtain sale price",
    )

    def _get_supplierinfo_pricelist_price(self):
        self.ensure_one()
        sale_price = self.price
        if self.sale_markup:
            sale_price = (self.price + (self.price * (self.sale_markup / 100))) or 0.0
        return sale_price
