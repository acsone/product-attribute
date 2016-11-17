# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    product_label_ids = fields.Many2many(
        comodel_name='product.template.tag',
        string='Labels',
    )
