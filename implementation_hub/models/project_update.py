# -*- coding: utf-8 -*-
from odoo import fields, models


class ProjectUpdate(models.Model):
    _inherit = "project.update"

    implementation_hub_visible = fields.Boolean(
        string="Visible en Implementation Hub",
        default=False,
        copy=False,
        help="Solo se expone cuando el proyecto también está publicado.",
    )
