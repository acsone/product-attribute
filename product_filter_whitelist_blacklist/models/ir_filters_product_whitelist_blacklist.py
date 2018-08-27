# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class IrFiltersProductWhitelistBlacklist(models.Model):

    _name = 'ir.filters.product.whitelist.blacklist'

    ir_filter_id = fields.Many2one(
        'ir.filters',
        domain=[('model_id.model', '=', 'product.template')]
    )
    type = fields.Selection(
        selection=[('blacklist', 'Blacklist'), ('whitelist', 'Whitelist')]
    )
    product_template_id = fields.Many2one(
        'product.template',
        string='Product',
    )
