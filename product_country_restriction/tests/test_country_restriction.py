# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import CountryRestrictionCommon
from odoo.exceptions import ValidationError


class TestCountryRestriction(CountryRestrictionCommon):

    def test_restriction(self):
        self.assertEquals(
            self.restriction_1,
            self.au.product_country_restriction_ids,
        )

        self.assertEquals(
            self.restriction_2,
            self.kp.product_country_restriction_ids,
        )
        self.assertEquals(
            1,
            self.kp.product_country_restriction_count,
        )

        self.assertTrue(
            self.product_2._has_country_restriction(self.kp, '2018-03-20')
        )
        self.assertTrue(
            self.product_2._has_country_restriction(self.au, '2018-03-20')
        )

        self.assertFalse(
            self.product_2._has_country_restriction(self.be, '2018-03-20')
        )

        self.assertFalse(
            self.product_3._has_country_restriction(self.kp, '2018-03-20')
        )
        self.assertTrue(
            self.product_3._has_country_restriction(self.kp, '2018-09-20')
        )

        self.assertFalse(
            self.product_4._has_country_restriction(self.kp, '2018-02-27')
        )
        self.assertTrue(
            self.product_4._has_country_restriction(self.kp, '2018-08-25')
        )

    def test_restriction_change_date(self):
        with self.assertRaises(ValidationError):
            self.restriction_2.item_ids.write({
                'start_date': '2018-05-01'
            })
