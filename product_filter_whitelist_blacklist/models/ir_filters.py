# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.osv import expression


class IrFilters(models.Model):

    _inherit = 'ir.filters'

    product_blacklist_ids = fields.One2many(
        'ir.filters.product.whitelist.blacklist',
        'ir_filter_id',
        domain=[('type', '=', 'blacklist')],
        string='Blacklisted Products',
    )
    product_whitelist_ids = fields.One2many(
        'ir.filters.product.whitelist.blacklist',
        'ir_filter_id',
        domain=[('type', '=', 'whitelist')],
        string='Whitelisted Products',
    )

    @api.multi
    def _get_eval_domain(self):
        res = super(IrFilters, self)._get_eval_domain()
        if self.product_whitelist_ids and self.product_blacklist_ids:
            result_domain = expression.AND([
                [('id', 'in', self.product_whitelist_ids.ids)],
                [('id', 'not in', self.product_blacklist_ids.ids)],
            ])
        elif self.product_blacklist_ids and not self.product_whitelist_ids:
            result_domain = [
                ('id', 'not in', self.product_blacklist_ids.ids)
            ]
        elif self.product_whitelist_ids and not self.product_blacklist_ids:
            result_domain = [
                ('id', 'in', self.product_whitelist_ids.ids)
            ]
        res = expression.AND([
            result_domain,
            res,
            ]
        )
        return res

    @api.multi
    def _get_products_whitelist_blacklist(self):
        self.ensure_one()
        template_obj = self.env['product.template']
        domain = self._get_eval_domain()
        return template_obj.search(domain)
