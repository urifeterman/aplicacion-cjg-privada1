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
        ("publish", "Publicado"),
        ("unpublish", "Despublicado"),
        ("scope_change", "Cambio de alcance"),
    ], string="Acción", required=True, readonly=True)
    previous_scope = fields.Selection([
        ("implementation", "Implementación"),
        ("support", "Soporte"),
    ], string="Alcance anterior", readonly=True)
    new_scope = fields.Selection([
        ("implementation", "Implementación"),
        ("support", "Soporte"),
    ], string="Nuevo alcance", readonly=True)
    published = fields.Boolean(string="Publicado después del cambio", readonly=True)
    changed_by = fields.Many2one(
        "res.users", string="Realizado por", required=True,
        readonly=True, default=lambda self: self.env.user,
    )
    changed_at = fields.Datetime(
        string="Fecha", required=True, readonly=True,
        default=fields.Datetime.now,
    )
