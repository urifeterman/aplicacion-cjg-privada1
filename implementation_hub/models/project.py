# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, ValidationError


class ProjectProject(models.Model):
    _inherit = "project.project"

    implementation_hub_published = fields.Boolean(
        string="Publicado en Implementation Hub", default=False,
        copy=False, tracking=True,
    )
    implementation_hub_scope = fields.Selection(
        [("implementation", "Implementación"), ("support", "Soporte")],
        string="Alcance del Hub", copy=False, tracking=True,
    )
    implementation_hub_progress_mode = fields.Selection(
        [("milestones", "Hitos publicados"), ("tasks", "Tareas publicadas")],
        string="Regla de avance del Hub", copy=False, tracking=True,
        help="Debe elegirse expresamente por proyecto. No se aplica una regla por defecto.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        protected = {
            "implementation_hub_published",
            "implementation_hub_scope",
            "implementation_hub_progress_mode",
        }
        if any(protected.intersection(vals) for vals in vals_list) and not self.env.user.has_group("project.group_project_manager"):
            raise AccessError(_("Solo un administrador de Proyectos puede configurar Implementation Hub."))
        return super().create(vals_list)

    @api.constrains(
        "implementation_hub_published",
        "implementation_hub_scope",
        "implementation_hub_progress_mode",
    )
    def _check_implementation_hub_publication(self):
        for project in self:
            if project.implementation_hub_published:
                if not project.implementation_hub_scope:
                    raise ValidationError(_("Selecciona el alcance antes de publicar."))
                if not project.implementation_hub_progress_mode:
                    raise ValidationError(_("Selecciona una regla de avance antes de publicar."))

    def write(self, vals):
        protected = {
            "implementation_hub_published",
            "implementation_hub_scope",
            "implementation_hub_progress_mode",
        }
        if protected.intersection(vals) and not self.env.user.has_group("project.group_project_manager"):
            raise AccessError(_("Solo un administrador de Proyectos puede configurar Implementation Hub."))
        tracked = {"implementation_hub_published", "implementation_hub_scope"}
        previous = {}
        if tracked.intersection(vals):
            previous = {
                rec.id: (rec.implementation_hub_published, rec.implementation_hub_scope or False)
                for rec in self
            }
        result = super().write(vals)
        if previous:
            values = []
            for rec in self:
                old_published, old_scope = previous[rec.id]
                new_published = rec.implementation_hub_published
                new_scope = rec.implementation_hub_scope or False
                if (old_published, old_scope) == (new_published, new_scope):
                    continue
                action = (
                    "publish" if new_published else "unpublish"
                ) if old_published != new_published else "scope_change"
                values.append({
                    "project_id": rec.id,
                    "action": action,
                    "previous_scope": old_scope,
                    "new_scope": new_scope,
                    "published": new_published,
                    "changed_by": self.env.user.id,
                })
            if values:
                self.env["implementation.hub.publication.log"].create(values)
        return result

    def _implementation_hub_progress(self):
        self.ensure_one()
        if self.implementation_hub_progress_mode == "milestones":
            records = self.env["project.milestone"].search([
                ("project_id", "=", self.id),
                ("implementation_hub_visible", "=", True),
            ])
            total = len(records)
            done = len(records.filtered("is_reached"))
            basis = "milestones"
        elif self.implementation_hub_progress_mode == "tasks":
            records = self.env["project.task"].search([
                ("project_id", "=", self.id),
                ("active", "=", True),
                ("implementation_hub_visible", "=", True),
            ])
            total = len(records)
            # Odoo 18: 1_done is terminal success; 1_canceled is not completed work.
            done = len(records.filtered(lambda task: task.state == "1_done"))
            basis = "tasks"
        else:
            return {"value": None, "done": 0, "total": 0, "basis": False, "reason": "not_configured"}
        if not total:
            return {"value": None, "done": 0, "total": 0, "basis": basis, "reason": "no_published_records"}
        return {
            "value": round(done * 100 / total),
            "done": done,
            "total": total,
            "basis": basis,
            "reason": False,
        }
