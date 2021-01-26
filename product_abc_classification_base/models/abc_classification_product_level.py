# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AbcClassificationProductLevel(models.Model):
    _name = "abc.classification.product.level"
    _inherit = "mail.thread"
    _description = "Abc Classification Product Level"

    display_name = fields.Char(compute="_compute_display_name")

    manual_level_id = fields.Many2one(
        "abc.classification.level",
        string="Manual classification level",
        track_visibility="onchange",
    )
    computed_level_id = fields.Many2one(
        "abc.classification.level",
        string="Computed classification level",
        track_visibility="onchange",
        readonly=True,
    )
    level_id = fields.Many2one(
        "abc.classification.level",
        string="Classification level",
        compute="_compute_level_id",
        store=True,
    )
    flag = fields.Boolean(
        default=False,
        compute="_compute_flag",
        string="If True, this means that the manual classification is "
        "different from the computed one",
    )
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        index=True,
        readonly=True,
        required=True,
        ondelete="cascade",
    )
    product_tmpl_id = fields.Many2one(
        "product.template",
        string="Product template",
        index=True,
        readonly=True,
    )
    # percentage
    profile_id = fields.Many2one(
        "abc.classification.profile",
        string="Profile",
        readonly=True,
        required=True,
    )

    _sql_constraints = [
        (
            "product_level_uniq",
            "UNIQUE(profile_id, product_id)",
            _("Only one level by profile by product allowed"),
        )
    ]

    @api.constrains("computed_level_id", "manual_level_id", "product_id")
    def _check_level(self):
        for rec in self:
            if not rec.computed_level_id and not rec.manual_level_id:
                raise ValidationError(_("Classification level is mandatory"))
            if (
                rec.computed_level_id
                and rec.computed_level_id.profile_id != rec.profile_id
            ):
                raise ValidationError(
                    _(
                        "Computed level must be in  the same classifiation "
                        "profile as the one on the product level"
                    )
                )
            if (
                rec.manual_level_id
                and rec.manual_level_id.profile_id != rec.profile_id
            ):
                raise ValidationError(
                    _(
                        "Manual level must be in  the same classifiation "
                        "profile as the one on the product level"
                    )
                )

    @api.depends("level_id", "profile_id")
    def _compute_display_name(self):
        for record in self:
            record.display_name = u"{profile_name}: {level_name}".format(
                profile_name=record.profile_id.name,
                level_name=record.level_id.name,
            )

    @api.depends("manual_level_id", "computed_level_id")
    def _compute_level_id(self):
        for rec in self:
            if rec.manual_level_id:
                rec.level_id = rec.manual_level_id
            else:
                rec.level_id = rec.computed_level_id

    @api.depends("manual_level_id", "computed_level_id")
    def _compute_flag(self):
        for rec in self:
            rec.flag = (
                rec.computed_level_id
                and rec.manual_level_id != rec.computed_level_id
            )

    @api.model
    def create(self, vals):
        if "manual_level_id" not in vals and "computed_level_id" in vals:
            # at creation the manual level is set to the same value as the
            # computed one
            vals["manual_level_id"] = vals["computed_level_id"]
        return super(AbcClassificationProductLevel, self).create(vals)
