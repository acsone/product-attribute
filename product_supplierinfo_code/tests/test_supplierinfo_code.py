# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSupplierinfoCode(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.supplier_1 = cls.env["res.partner"].create({"name": "Supplier 1"})
        cls.supplier_2 = cls.env["res.partner"].create({"name": "Supplier 2"})

        cls.product = cls.env["product.template"].create(
            {
                "name": "Test Product",
            }
        )

        cls.product_supplierinfo = cls.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": cls.product.id,
                "partner_id": cls.supplier_1.id,
                "delay": 3,
                "min_qty": 1,
                "price": 750,
                "currency_id": cls.env.ref("base.USD").id,
                "product_code": "CODE1",
                "sequence": 1,
            }
        )

        cls.product_supplierinfo2 = cls.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": cls.product.id,
                "partner_id": cls.supplier_2.id,
                "delay": 3,
                "min_qty": 1,
                "price": 790,
                "currency_id": cls.env.ref("base.USD").id,
                "product_code": "CODE2",
                "sequence": 10,
            }
        )

        cls.product.invalidate_recordset(["seller_ids", "supplier_product_code"])

    def test_supplierinfo_code(self):
        """
        Check if first supplier product code is CODE1
        Search for product based on supplier_product_code
        """
        self.assertEqual(self.product.supplier_product_code, "CODE1")

        product = self.product.search(
            [
                ("id", "=", self.product.id),
                ("supplier_product_code", "=", "CODE1"),
            ]
        )
        self.assertEqual(product, self.product)

        product = self.product.search(
            [
                ("id", "=", self.product.id),
                ("supplier_product_code", "=", "CODE2"),
            ]
        )
        self.assertEqual(product, self.product)
