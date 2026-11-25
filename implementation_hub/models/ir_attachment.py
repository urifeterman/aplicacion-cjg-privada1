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

    def _implementation_hub_parent_project(self):
        self.ensure_one()
        if not self.res_model or not self.res_id:
            return self.env["project.project"]
        if self.res_model == "project.project":
            return self.env["project.project"].browse(self.res_id).exists()
        if self.res_model in ("project.task", "project.milestone", "project.update"):
            parent = self.env[self.res_model].browse(self.res_id).exists()
            return parent.project_id if parent else self.env["project.project"]
        return self.env["project.project"]

    @api.model_create_multi
    def create(self, vals_list):
        if any(vals.get("implementation_hub_visible") for vals in vals_list) and not self.env.user.has_group("project.group_project_manager"):
            raise AccessError(_("Solo un administrador de Proyectos puede publicar documentos en Implementation Hub."))
        records = super().create(vals_list)
        for record in records.filtered("implementation_hub_visible"):
            project = record._implementation_hub_parent_project()
            if project:
                project._implementation_hub_log_resource(
                    record._name, record.id, record.name, True
                )
        return records

    def write(self, vals):
        if "implementation_hub_visible" in vals and not self.env.user.has_group("project.group_project_manager"):
            raise AccessError(_("Solo un administrador de Proyectos puede cambiar la publicación de documentos."))
        previous = {record.id: record.implementation_hub_visible for record in self}
        result = super().write(vals)
        if "implementation_hub_visible" in vals:
            for record in self:
                if previous[record.id] != record.implementation_hub_visible:
                    project = record._implementation_hub_parent_project()
                    if project:
                        project._implementation_hub_log_resource(
                            record._name,
                            record.id,
                            record.name,
                            record.implementation_hub_visible,
                        )
        return result
