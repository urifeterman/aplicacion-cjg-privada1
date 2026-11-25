# -*- coding: utf-8 -*-
from odoo import fields, http
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import request
from odoo.osv.expression import OR


class ImplementationHubController(http.Controller):

    STATUS_LABELS = {
        "on_track": "En curso",
        "at_risk": "En riesgo",
        "off_track": "Fuera de plan",
        "on_hold": "En pausa",
        "to_define": "Sin actualización publicada",
        "done": "Finalizado",
    }
    TASK_STATE_LABELS = {
        "01_in_progress": "En progreso",
        "02_changes_requested": "Cambios solicitados",
        "03_approved": "Aprobada",
        "1_done": "Finalizada",
        "1_canceled": "Cancelada",
        "04_waiting_normal": "En espera",
    }
    PARENT_MODELS = {
        "project.project",
        "project.task",
        "project.milestone",
        "project.update",
    }

    def _is_portal_user(self):
        user = request.env.user
        return not user._is_public() and user.has_group("base.group_portal")

    def _portal_projects(self):
        """Search in the current user's environment; record rules remain active."""
        projects = request.env["project.project"].search([
            ("implementation_hub_published", "=", True),
            ("partner_id", "!=", False),
            ("privacy_visibility", "=", "portal"),
            ("active", "=", True),
        ], order="date asc, name asc")

        user_partner = request.env.user.partner_id
        user_company = user_partner.commercial_partner_id
        result = projects.browse()
        for project in projects:
            same_company = project.partner_id.commercial_partner_id == user_company
            collaborator = bool(project.collaborator_ids.filtered(
                lambda item: item.partner_id == user_partner
            ))
            if same_company or collaborator:
                result |= project
        return result

    @http.route(
        ["/implementation-hub", "/implementation-hub/"],
        type="http", auth="user", methods=["GET"],
        website=True, sitemap=False,
    )
    def home(self, **kwargs):
        if request.httprequest.path == "/implementation-hub":
            return request.redirect("/implementation-hub/")
        if not self._is_portal_user():
            return request.not_found()
        response = request.render("implementation_hub.portal_app", {})
        response.headers["Cache-Control"] = "private, no-store"
        response.headers["Pragma"] = "no-cache"
        return response

    @http.route(
        "/implementation-hub/data",
        type="http", auth="user", methods=["GET"],
        website=True, sitemap=False, readonly=True,
    )
    def data(self, **kwargs):
        if not self._is_portal_user():
            return request.not_found()

        projects = self._portal_projects()
        project_data = [self._project_payload(project) for project in projects]
        payload = {
            "profile": {
                "name": request.env.user.partner_id.name or "",
                "email": request.env.user.partner_id.email or "",
                "company": request.env.user.partner_id.commercial_partner_id.name or "",
            },
            "summary": {
                "total": len(project_data),
                "active": sum(item["status"] != "done" for item in project_data),
                "done": sum(item["status"] == "done" for item in project_data),
                "delayed": sum(item["delayed"] for item in project_data),
            },
            "projects": project_data,
            "generated_at": fields.Datetime.to_string(fields.Datetime.now()),
        }
        response = request.make_json_response(payload)
        response.headers["Cache-Control"] = "private, no-store"
        response.headers["Pragma"] = "no-cache"
        return response

    def _project_payload(self, project):
        tasks = request.env["project.task"].search([
            ("project_id", "=", project.id),
            ("active", "=", True),
            ("implementation_hub_visible", "=", True),
        ], order="date_deadline asc, id asc")
        milestones = request.env["project.milestone"].search([
            ("project_id", "=", project.id),
            ("implementation_hub_visible", "=", True),
        ], order="deadline asc, id asc")
        updates = request.env["project.update"].search([
            ("project_id", "=", project.id),
            ("implementation_hub_visible", "=", True),
        ], order="date desc, id desc")

        progress = project._implementation_hub_progress()
        # Never derive a public status from project.last_update_status: that field
        # can reflect an update which the team has not published to this customer.
        status = updates[0].status if updates else "to_define"
        today = fields.Date.context_today(project)
        # A delay is not asserted until an explicit public status exists; otherwise
        # the Hub cannot safely infer whether the project was completed privately.
        delayed = bool(project.date and project.date < today and updates and status != "done")

        task_data = [{
            "title": task.name,
            "stage": task.stage_id.display_name or "",
            "state": task.state,
            "state_label": self.TASK_STATE_LABELS.get(task.state, "En progreso"),
            "deadline": fields.Datetime.to_string(task.date_deadline) if task.date_deadline else None,
            "updated_at": fields.Datetime.to_string(task.write_date) if task.write_date else None,
        } for task in tasks]

        milestone_data = [{
            "title": milestone.name,
            "deadline": fields.Date.to_string(milestone.deadline) if milestone.deadline else None,
            "reached": bool(milestone.is_reached),
            "reached_date": fields.Date.to_string(milestone.reached_date) if milestone.reached_date else None,
            "updated_at": fields.Datetime.to_string(milestone.write_date) if milestone.write_date else None,
        } for milestone in milestones]

        update_data = [{
            "title": update.name,
            "status": update.status,
            "status_label": self.STATUS_LABELS.get(update.status, update.status),
            "date": fields.Date.to_string(update.date) if update.date else None,
            "updated_at": fields.Datetime.to_string(update.write_date) if update.write_date else None,
        } for update in updates]

        timeline = []
        for item in task_data:
            timeline.append({
                "kind": "task", "title": item["title"],
                "date": item["deadline"] or item["updated_at"],
                "status": item["state_label"],
            })
        for item in milestone_data:
            timeline.append({
                "kind": "milestone", "title": item["title"],
                "date": item["deadline"] or item["reached_date"],
                "status": "Completado" if item["reached"] else "Pendiente",
            })
        for item in update_data:
            timeline.append({
                "kind": "update", "title": item["title"],
                "date": item["date"], "status": item["status_label"],
            })
        for item in self._public_comments(project, tasks):
            timeline.append({
                "kind": "comment", "title": item["author"],
                "date": item["date"], "status": item["preview"],
            })
        timeline.sort(key=lambda item: item["date"] or "", reverse=True)

        last_updated_candidates = [
            item["updated_at"] for item in task_data + milestone_data + update_data
            if item.get("updated_at")
        ]
        last_updated_candidates.extend(
            item["date"] for item in timeline
            if item["kind"] == "comment" and item.get("date")
        )
        last_updated = max(last_updated_candidates, default=None)

        now = fields.Datetime.now()
        next_task = next((
            task for task in tasks
            if task.date_deadline and task.date_deadline >= now
        ), None)

        return {
            "id": project.id,
            "name": project.name,
            "scope": project.implementation_hub_scope,
            "scope_label": dict(project._fields["implementation_hub_scope"].selection).get(
                project.implementation_hub_scope, ""
            ),
            "status": status,
            "status_label": self.STATUS_LABELS.get(status, status),
            "progress": progress,
            "start_date": fields.Date.to_string(project.date_start) if project.date_start else None,
            "end_date": fields.Date.to_string(project.date) if project.date else None,
            "delayed": delayed,
            "last_updated": last_updated,
            "next_activity": {
                "title": next_task.name,
                "deadline": fields.Datetime.to_string(next_task.date_deadline),
            } if next_task else None,
            "tasks": task_data,
            "milestones": milestone_data,
            "updates": update_data,
            "timeline": timeline,
            "documents": self._published_documents(project, tasks, milestones, updates),
        }

    def _public_comments(self, project, tasks):
        """Only public comments; internal notes and unrelated resources are excluded."""
        domains = [[
            ("model", "=", "project.project"),
            ("res_id", "=", project.id),
        ]]
        if tasks:
            domains.append([
                ("model", "=", "project.task"),
                ("res_id", "in", tasks.ids),
            ])
        try:
            messages = request.env["mail.message"].search(
                OR(domains) + [
                    ("message_type", "=", "comment"),
                    ("is_internal", "=", False),
                ],
                order="date desc, id desc",
                limit=100,
            )
        except AccessError:
            return []
        return [{
            "author": message.author_id.name or message.email_from or "Equipo",
            "date": fields.Datetime.to_string(message.date) if message.date else None,
            "preview": message.preview or "",
        } for message in messages]

    def _published_documents(self, project, tasks, milestones, updates):
        per_model = [
            ("project.project", [project.id]),
            ("project.task", tasks.ids),
            ("project.milestone", milestones.ids),
            ("project.update", updates.ids),
        ]
        domains = [
            [("res_model", "=", model_name), ("res_id", "in", ids)]
            for model_name, ids in per_model if ids
        ]
        if not domains:
            return []
        try:
            # Narrow sudo is required because Odoo's base ir.attachment ACL intentionally
            # denies direct Portal searches. Every parent resource in these domains was
            # already selected under the current Portal user's ACLs and record rules.
            attachments = request.env["ir.attachment"].sudo().search(
                OR(domains) + [
                    ("implementation_hub_visible", "=", True),
                    ("type", "=", "binary"),
                ],
                order="name asc",
                limit=100,
            )
        except AccessError:
            return []
        return [{
            "id": attachment.id,
            "name": attachment.name,
            "url": "/implementation-hub/document/%s" % attachment.id,
            "mimetype": attachment.mimetype or "",
        } for attachment in attachments]

    @http.route(
        "/implementation-hub/document/<int:attachment_id>",
        type="http", auth="user", methods=["GET"],
        website=True, sitemap=False, readonly=True,
    )
    def document(self, attachment_id, **kwargs):
        if not self._is_portal_user():
            return request.not_found()
        try:
            # Odoo 18's base attachment ACL does not let Portal users search
            # ir.attachment directly. Read the metadata under sudo only for this
            # supplied attachment ID, then validate the parent record as the
            # actual Portal user before streaming any binary content.
            attachment = request.env["ir.attachment"].sudo().browse(attachment_id).exists()
            if not attachment or not attachment.implementation_hub_visible:
                return request.not_found()
            if attachment.res_model not in self.PARENT_MODELS or not attachment.res_id:
                return request.not_found()

            linked = request.env[attachment.res_model].browse(attachment.res_id).exists()
            if not linked:
                return request.not_found()
            linked.check_access("read")

            if attachment.res_model == "project.project":
                project = linked
                resource_visible = True
            else:
                project = linked.project_id
                resource_visible = bool(linked.implementation_hub_visible)
            if not project:
                return request.not_found()
            project.check_access("read")
            if (
                not resource_visible
                or not project.implementation_hub_published
                or not project.partner_id
            ):
                return request.not_found()

            user_partner = request.env.user.partner_id
            same_company = (
                project.partner_id.commercial_partner_id
                == user_partner.commercial_partner_id
            )
            collaborator = bool(project.collaborator_ids.filtered(
                lambda item: item.partner_id == user_partner
            ))
            if not (same_company or collaborator):
                return request.not_found()

            stream = request.env["ir.binary"].sudo()._get_stream_from(
                attachment, field_name="raw",
            )
            response = stream.get_response(as_attachment=True, max_age=0)
            response.headers["Cache-Control"] = "private, no-store"
            response.headers["Pragma"] = "no-cache"
            return response
        except (AccessError, MissingError, UserError, KeyError):
            return request.not_found()

    @http.route(
        "/implementation-hub/manifest.webmanifest",
        type="http", auth="public", methods=["GET"],
        csrf=False, sitemap=False,
    )
    def manifest(self, **kwargs):
        return request.make_json_response({
            "name": "Implementation Hub",
            "short_name": "Hub",
            "start_url": "/implementation-hub/",
            "scope": "/implementation-hub/",
            "display": "standalone",
            "background_color": "#f5f7fb",
            "theme_color": "#172554",
            "icons": [{
                "src": "/implementation_hub/static/description/icon.svg",
                "sizes": "any",
                "type": "image/svg+xml",
                "purpose": "any",
            }],
        })

    @http.route(
        "/implementation-hub/service-worker.js",
        type="http", auth="public", methods=["GET"],
        csrf=False, sitemap=False,
    )
    def service_worker(self, **kwargs):
        script = r'''
const CACHE_NAME = "implementation-hub-offline-v1";
const OFFLINE_URL = "/implementation-hub/offline";

self.addEventListener("install", (event) => {
    event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.add(OFFLINE_URL)));
    self.skipWaiting();
});
self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((keys) => Promise.all(
            keys.filter((key) => key.startsWith("implementation-hub-") && key !== CACHE_NAME)
                .map((key) => caches.delete(key))
        )).then(() => self.clients.claim())
    );
});
self.addEventListener("fetch", (event) => {
    const req = event.request;
    if (req.method !== "GET" || req.mode !== "navigate") return;
    const url = new URL(req.url);
    if (url.origin !== self.location.origin || !url.pathname.startsWith("/implementation-hub/")) return;
    event.respondWith(fetch(req).catch(async () => (await caches.match(OFFLINE_URL)) || Response.error()));
});
'''
        return request.make_response(script, headers=[
            ("Content-Type", "application/javascript; charset=utf-8"),
            ("Service-Worker-Allowed", "/implementation-hub/"),
            ("Cache-Control", "no-cache"),
        ])

    @http.route(
        "/implementation-hub/offline",
        type="http", auth="public", methods=["GET"],
        csrf=False, sitemap=False,
    )
    def offline(self, **kwargs):
        page = """<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#172554">
<title>Sin conexión · Implementation Hub</title>
<style>
body{font-family:system-ui,sans-serif;background:#f5f7fb;color:#172033;display:grid;min-height:100vh;place-items:center;margin:0}
main{max-width:34rem;padding:2rem;text-align:center}h1{font-size:1.7rem}p{line-height:1.6;color:#536078}
</style></head><body><main><h1>Sin conexión</h1>
<p>No hay conexión con Odoo. Los datos privados no se guardan en este dispositivo.
Vuelve a conectarte para consultar la información actualizada.</p>
<a href="/implementation-hub/">Reintentar</a></main></body></html>"""
        return request.make_response(page, headers=[
            ("Content-Type", "text/html; charset=utf-8"),
            ("Cache-Control", "public, max-age=0"),
        ])
