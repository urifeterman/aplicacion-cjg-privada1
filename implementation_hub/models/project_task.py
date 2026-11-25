# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import AccessError


class ProjectTask(models.Model):
    _inherit = "project.task"

    implementation_hub_visible = fields.Boolean(
        string="Visible en Implementation Hub",
        default=False,
        copy=False,
        help="Solo se publica si el proyecto asociado también está publicado.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        if any(vals.get("implementation_hub_visible") for vals in vals_list) and not self.env.user.has_group("project.group_project_manager"):
            raise AccessError(_("Solo un administrador de Proyectos puede publicar tareas en Implementation Hub."))
        records = super().create(vals_list)
        for record in records.filtered("implementation_hub_visible"):
            if record.project_id:
                record.project_id._implementation_hub_log_resource(
                    record._name, record.id, record.display_name, True
                )
        return records

    def write(self, vals):
        if "implementation_hub_visible" in vals and not self.env.user.has_group("project.group_project_manager"):
            raise AccessError(_("Solo un administrador de Proyectos puede cambiar la publicación en Implementation Hub."))
        previous = {record.id: record.implementation_hub_visible for record in self}
        result = super().write(vals)
        if "implementation_hub_visible" in vals:
            for record in self:
                if previous[record.id] != record.implementation_hub_visible and record.project_id:
                    record.project_id._implementation_hub_log_resource(
                        record._name,
                        record.id,
                        record.display_name,
                        record.implementation_hub_visible,
                    )
        return result
