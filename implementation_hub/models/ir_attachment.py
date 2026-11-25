# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import AccessError


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    implementation_hub_visible = fields.Boolean(
        string="Visible en Implementation Hub",
        default=False,
        copy=False,
        help="La descarga vuelve a validar el acceso al adjunto y al registro vinculado.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        if any(vals.get("implementation_hub_visible") for vals in vals_list) and not self.env.user.has_group("project.group_project_manager"):
            raise AccessError(_("Solo un administrador de Proyectos puede publicar documentos en Implementation Hub."))
        return super().create(vals_list)

    def write(self, vals):
        if "implementation_hub_visible" in vals and not self.env.user.has_group("project.group_project_manager"):
            raise AccessError(_("Solo un administrador de Proyectos puede cambiar la publicación de documentos."))
        return super().write(vals)
