# Copyright 2024 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_field_renames = [
    ("product.supplierinfo", "product_supplierinfo", "sale_margin", "sale_markup"),
]

_xmlid_renames = [
    (
        "product_pricelist_supplierinfo.group_supplierinfo_pricelist_sale_margin",
        "product_pricelist_supplierinfo.group_supplierinfo_pricelist_sale_markup",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
