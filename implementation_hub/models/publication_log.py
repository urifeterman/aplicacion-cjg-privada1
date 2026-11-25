# -*- coding: utf-8 -*-
from odoo import fields, models


class ImplementationHubPublicationLog(models.Model):
    _name = "implementation.hub.publication.log"
    _description = "Historial de publicación de Implementation Hub"
    _order = "changed_at desc, id desc"

    project_id = fields.Many2one(
        "project.project", string="Proyecto", required=True,
        ondelete="cascade", index=True,
    )
    action = fields.Selection([
        ("publish", "Proyecto publicado"),
        ("unpublish", "Proyecto despublicado"),
        ("scope_change", "Cambio de alcance"),
        ("publish_resource", "Recurso publicado"),
        ("unpublish_resource", "Recurso despublicado"),
    ], string="Acción", required=True, readonly=True)
    resource_model = fields.Char(string="Modelo del recurso", readonly=True, index=True)
    resource_id = fields.Many2oneReference(
        string="ID del recurso", model_field="resource_model", readonly=True,
    )
    resource_name = fields.Char(string="Recurso", readonly=True)
    previous_scope = fields.Selection([
        ("implementation", "Implementación"),
        ("support", "Soporte"),
    ], string="Alcance anterior", readonly=True)
    new_scope = fields.Selection([
        ("implementation", "Implementación"),
        ("support", "Soporte"),
    ], string="Nuevo alcance", readonly=True)
    published = fields.Boolean(string="Proyecto publicado después del cambio", readonly=True)
    changed_by = fields.Many2one(
        "res.users", string="Realizado por", required=True,
        readonly=True, default=lambda self: self.env.user,
    )
    changed_at = fields.Datetime(
        string="Fecha", required=True, readonly=True,
        default=fields.Datetime.now,
    )
