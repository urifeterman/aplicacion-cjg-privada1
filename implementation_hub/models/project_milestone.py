# -*- coding: utf-8 -*-
from odoo import fields, models


class ProjectMilestone(models.Model):
    _inherit = "project.milestone"

    implementation_hub_visible = fields.Boolean(
        string="Visible en Implementation Hub", default=False, copy=False,
    )
