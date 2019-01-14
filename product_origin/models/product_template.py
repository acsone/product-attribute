# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    country_id = fields.Many2one(
        comodel_name='res.country',
        string='Country of Origin',
        ondelete='restrict',
        index=True,
    )

    state_id = fields.Many2one(
        comodel_name='res.country.state',
        string='Country State of Origin',
        ondelete='restrict',
        index=True,
    )

    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id:
            if self.state_id and \
                    self.state_id.country_id != self.country_id:
                self.state_id = False
            return {'domain': {
                'state_id': [('country_id', '=', self.country_id.id)],
            }}
