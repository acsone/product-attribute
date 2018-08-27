# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Product Filter Whitelist Blacklist',
    'summary': """
        Adds the ability to add products to blacklist or whitelist 
        products filters (new method on filter object).
        This has no influence on interface filtering""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://acsone.eu',
    'depends': [
        'base',
        'product',
    ],
    'data': [
        'views/ir_filters.xml',
        'security/security.xml',
    ],
}
