# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestImplementationHubPublication(TransactionCase):

    def test_publication_requires_explicit_scope(self):
        project = self.env["project.project"].create({
            "name": "Hub test without scope",
            "implementation_hub_progress_mode": "tasks",
        })
        with self.assertRaises(ValidationError):
            project.write({"implementation_hub_published": True})

    def test_publication_requires_explicit_progress_mode(self):
        project = self.env["project.project"].create({
            "name": "Hub test without progress mode",
            "implementation_hub_scope": "implementation",
        })
        with self.assertRaises(ValidationError):
            project.write({"implementation_hub_published": True})

    def test_project_without_customer_can_be_marked_but_is_not_in_portal_domain(self):
        project = self.env["project.project"].create({
            "name": "Hub test without customer",
            "implementation_hub_scope": "implementation",
            "implementation_hub_progress_mode": "tasks",
        })
        project.write({"implementation_hub_published": True})
        visible = self.env["project.project"].search([
            ("id", "=", project.id),
            ("implementation_hub_published", "=", True),
            ("partner_id", "!=", False),
            ("privacy_visibility", "=", "portal"),
        ])
        self.assertFalse(visible)

    def test_progress_is_unavailable_when_no_published_records(self):
        project = self.env["project.project"].create({
            "name": "Hub test empty denominator",
            "implementation_hub_scope": "implementation",
            "implementation_hub_progress_mode": "tasks",
        })
        result = project._implementation_hub_progress()
        self.assertIsNone(result["value"])
        self.assertEqual(result["reason"], "no_published_records")
