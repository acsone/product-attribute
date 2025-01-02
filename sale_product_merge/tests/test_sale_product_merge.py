# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.product_merge.tests.test_product_merge import TestProductMerge


class TestSaleProductMerge(TestProductMerge):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Test Pricelist",
                "item_ids": [
                    Command.create(
                        {
                            "applied_on": "1_product",
                            "product_tmpl_id": cls.product_r.id,
                            "fixed_price": 70.0,
                        }
                    ),
                    Command.create(
                        {
                            "applied_on": "1_product",
                            "product_tmpl_id": cls.product_b.id,
                            "fixed_price": 50.0,
                        }
                    ),
                ],
            }
        )

    def test_update_price_list(self):
        self.test_0()
        self.wizard.action_merge_products()
        self.assertEqual(self.pricelist.item_ids.product_tmpl_id, self.product_r)
        self.assertEqual(self.pricelist.item_ids[0].applied_on, "0_product_variant")
        self.assertEqual(
            self.pricelist.item_ids.product_id, self.variant_r | self.variant_b
        )
