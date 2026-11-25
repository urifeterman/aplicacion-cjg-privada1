# -*- coding: utf-8 -*-
{
    "name": "Implementation Hub",
    "summary": "Portal privado de seguimiento de implementaciones Odoo",
    "version": "18.0.1.0.0",
    "category": "Services/Project",
    "author": "CJG",
    "license": "LGPL-3",
    "depends": ["base", "web", "portal", "project", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/implementation_hub_security.xml",
        "views/backend_views.xml",
        "views/portal_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "implementation_hub/static/src/portal/app.js",
            "implementation_hub/static/src/portal/app.xml",
            "implementation_hub/static/src/portal/app.scss",
        ],
    },
    "application": True,
    "installable": True,
    "auto_install": False,
}
