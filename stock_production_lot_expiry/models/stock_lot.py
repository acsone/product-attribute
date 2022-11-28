# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import _, api, fields, models
from odoo.osv.expression import NEGATIVE_TERM_OPERATORS


class StockProductionLot(models.Model):

    _inherit = "stock.lot"

    is_expired = fields.Boolean(
        compute="_compute_is_expired", search="_search_is_expired"
    )

    expiry_date = fields.Datetime(
        compute="_compute_expiry_date", store=True, index=True
    )

    @api.model
    def _selection_expiry_date_field(self):
        return [
            ("use_date", _("Use date")),
            ("expiration_date", _("End of Life Date")),
            ("alert_date", _("Alert date")),
            ("removal_date", _("Removal date")),
        ]

    @api.depends(lambda self: self._expiry_date_depends())
    def _compute_expiry_date(self):
        for rec in self:
            rec.expiry_date = rec[rec.product_id.lot_expiry_field_name]

    def _search_is_expired(self, operator, value):
        search_expired = (
            # is_expired != False
            (operator in NEGATIVE_TERM_OPERATORS and not value)
            # or is_expired = True
            or (operator not in NEGATIVE_TERM_OPERATORS and value)
        )
        if search_expired:
            return [("expiry_date", "<", fields.Datetime.now())]
        return [
            "|",
            ("expiry_date", "=", False),
            ("expiry_date", ">=", fields.Datetime.now()),
        ]

    @api.model
    def _expiry_date_depends(self):
        return [f[0] for f in self._selection_expiry_date_field()]

    @api.depends("expiry_date")
    def _compute_is_expired(self):
        for rec in self:
            rec.is_expired = rec.expiry_date and rec.expiry_date < datetime.now()
