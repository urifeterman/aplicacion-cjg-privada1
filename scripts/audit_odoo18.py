# -*- coding: utf-8 -*-
"""
Read-only Odoo 18 audit for Implementation Hub.

Run inside an authenticated Odoo shell where the variable env is available.
This script does not create, write, unlink, or export customer names/content.
It prints a JSON inventory of installed modules, model/field availability,
Portal users (counts only), ACLs, record rules, and relevant record counts.
"""
import json
from datetime import datetime, timezone

from odoo import release


def model_exists(model_name):
    return model_name in env.registry.models


def present_fields(model_name, field_names):
    if not model_exists(model_name):
        return {"model_exists": False, "fields": {}}
    model = env[model_name]
    return {
        "model_exists": True,
        "fields": {name: name in model._fields for name in field_names},
    }


def safe_count(model_name, domain=None):
    if not model_exists(model_name):
        return None
    try:
        return env[model_name].search_count(domain or [])
    except Exception as exc:
        return {"error": type(exc).__name__}


def group_label(group):
    return group.display_name if group else "All users"


def main():
    installed_modules = env["ir.module.module"].search(
        [("state", "=", "installed")], order="name"
    )
    installed_by_name = {
        module.name: {
            "state": module.state,
            "version": module.installed_version or module.latest_version or "",
        }
        for module in installed_modules
    }

    target_modules = [
        "base", "web", "portal", "website", "mail", "project",
        "project_enterprise", "helpdesk", "documents",
    ]

    portal_group = env.ref("base.group_portal", raise_if_not_found=False)
    manager_group = env.ref("project.group_project_manager", raise_if_not_found=False)

    portal_user_domain = [("groups_id", "in", portal_group.ids)] if portal_group else []
    portal_users = (
        env["res.users"].with_context(active_test=False).search(portal_user_domain)
        if portal_group else env["res.users"]
    )

    model_fields = {
        "project.project": [
            "partner_id", "privacy_visibility", "collaborator_ids",
            "date_start", "date", "last_update_status", "allow_milestones",
            "implementation_hub_published", "implementation_hub_scope",
            "implementation_hub_progress_mode",
        ],
        "project.task": [
            "project_id", "active", "state", "stage_id", "date_deadline",
            "user_ids", "partner_id", "implementation_hub_visible",
        ],
        "project.milestone": [
            "project_id", "deadline", "is_reached", "reached_date",
            "implementation_hub_visible",
        ],
        "project.update": [
            "project_id", "name", "status", "date", "description",
            "implementation_hub_visible",
        ],
        "project.collaborator": [
            "project_id", "partner_id", "limited_access",
        ],
        "mail.message": [
            "model", "res_id", "message_type", "is_internal",
            "subtype_id", "author_id", "preview",
        ],
        "ir.attachment": [
            "res_model", "res_id", "type", "mimetype", "public",
            "access_token", "implementation_hub_visible",
        ],
        "helpdesk.ticket": [
            "name", "partner_id", "team_id", "stage_id", "priority",
            "user_id", "tag_ids", "company_id", "message_partner_ids",
        ],
        "helpdesk.team": [
            "name", "privacy", "company_id",
        ],
        "documents.document": [
            "name", "attachment_id", "folder_id", "owner_id",
        ],
        "documents.folder": [
            "name", "parent_folder_id", "company_id",
        ],
    }

    fields_report = {
        model_name: present_fields(model_name, fields)
        for model_name, fields in model_fields.items()
    }

    # Metadata for custom models/fields only. No field values are read.
    custom_models = []
    if "state" in env["ir.model"]._fields:
        custom_models = env["ir.model"].search([("state", "=", "manual")], order="model")
    custom_fields = []
    if "state" in env["ir.model.fields"]._fields:
        custom_fields = env["ir.model.fields"].search(
            [("state", "=", "manual")], order="model, name"
        )

    relevant_models = [name for name in model_fields if model_exists(name)]
    model_records = env["ir.model"].search([("model", "in", relevant_models)])
    model_id_by_name = {item.model: item.id for item in model_records}

    access_report = []
    if model_exists("ir.model.access"):
        access_rows = env["ir.model.access"].search([
            ("model_id", "in", list(model_id_by_name.values()))
        ], order="model_id, name")
        for row in access_rows:
            access_report.append({
                "model": row.model_id.model,
                "name": row.name,
                "group": group_label(row.group_id),
                "read": row.perm_read,
                "write": row.perm_write,
                "create": row.perm_create,
                "unlink": row.perm_unlink,
                "active": row.active,
            })

    rules_report = []
    if model_exists("ir.rule"):
        rule_rows = env["ir.rule"].search([
            ("model_id", "in", list(model_id_by_name.values()))
        ], order="model_id, name")
        for rule in rule_rows:
            rules_report.append({
                "model": rule.model_id.model,
                "name": rule.name,
                "groups": rule.groups.mapped("display_name"),
                "global": rule.global,
                "active": rule.active,
                "perm_read": rule.perm_read,
                "perm_write": rule.perm_write,
                "perm_create": rule.perm_create,
                "perm_unlink": rule.perm_unlink,
                "domain_force": rule.domain_force,
            })

    counts = {
        "project.project": safe_count("project.project"),
        "project.project_with_customer": safe_count(
            "project.project", [("partner_id", "!=", False)]
        ),
        "project.project_portal_visibility": safe_count(
            "project.project", [("privacy_visibility", "=", "portal")]
        ),
        "project.task": safe_count("project.task"),
        "project.milestone": safe_count("project.milestone"),
        "project.update": safe_count("project.update"),
        "helpdesk.ticket": safe_count("helpdesk.ticket"),
        "documents.document": safe_count("documents.document"),
        "documents.folder": safe_count("documents.folder"),
    }

    base_url = env["ir.config_parameter"].get_param("web.base.url") or ""
    report = {
        "audit": {
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "script_mode": "read_only",
            "odoo_version": getattr(release, "version", "unknown"),
            "odoo_version_info": list(getattr(release, "version_info", ())),
            "https_base_url_configured": base_url.lower().startswith("https://"),
        },
        "modules": {
            name: installed_by_name.get(name, {"state": "not_installed"})
            for name in target_modules
        },
        "portal": {
            "portal_group_found": bool(portal_group),
            "project_manager_group_found": bool(manager_group),
            "portal_user_count_including_archived": len(portal_users),
            "portal_user_active_count": len(portal_users.filtered("active")),
        },
        "models_and_fields": fields_report,
        "record_counts": counts,
        "custom_models": [
            {"model": item.model, "name": item.name, "state": item.state}
            for item in custom_models
        ],
        "custom_fields": [
            {
                "model": item.model,
                "name": item.name,
                "field_description": item.field_description,
                "ttype": item.ttype,
                "state": item.state,
            }
            for item in custom_fields
        ],
        "access_control_lists": access_report,
        "record_rules": rules_report,
    }

    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))


main()
