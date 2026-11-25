# -*- coding: utf-8 -*-
from odoo import fields, models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    implementation_hub_visible = fields.Boolean(
        string="Visible en Implementation Hub",
        default=False,
        copy=False,
        help="La descarga vuelve a validar el acceso del usuario al adjunto y al registro vinculado.",
    )
