/** @odoo-module **/

import { Component, onMounted, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class ImplementationHubPortal extends Component {
    static template = "implementation_hub.PortalApp";
    static props = {};

    setup() {
        this.state = useState({
            loading: true,
            error: false,
            data: null,
            section: "dashboard",
            selectedProjectId: null,
        });
        onWillStart(() => this.loadData());
        onMounted(() => this.registerServiceWorker());
    }

    async loadData() {
        this.state.loading = true;
        this.state.error = false;
        try {
            const response = await fetch("/implementation-hub/data", {
                method: "GET",
                credentials: "same-origin",
                headers: { Accept: "application/json" },
                cache: "no-store",
            });
            if (!response.ok) {
                throw new Error("No fue posible consultar Implementation Hub.");
            }
            this.state.data = await response.json();
        } catch {
            this.state.error = true;
            this.state.data = null;
        } finally {
            this.state.loading = false;
        }
    }

    async registerServiceWorker() {
        if (!("serviceWorker" in navigator)) {
            return;
        }
        try {
            await navigator.serviceWorker.register(
                "/implementation-hub/service-worker.js",
                { scope: "/implementation-hub/" }
            );
        } catch {
            // El Portal sigue funcionando si el navegador no admite la PWA.
        }
    }

    navigate(section) {
        this.state.section = section;
        this.state.selectedProjectId = null;
    }

    openProject(projectId) {
        this.state.section = "detail";
        this.state.selectedProjectId = projectId;
    }

    backToProjects() {
        this.state.section = "implementations";
        this.state.selectedProjectId = null;
    }

    get projects() {
        return this.state.data?.projects || [];
    }

    get summary() {
        return this.state.data?.summary || {
            total: 0, active: 0, done: 0, pending: 0, delayed: 0,
        };
    }

    get selectedProject() {
        return this.projects.find(
            (project) => project.id === this.state.selectedProjectId
        ) || null;
    }

    get documents() {
        return this.projects.flatMap((project) =>
            (project.documents || []).map((document) => ({
                ...document,
                project_name: project.name,
            }))
        );
    }

    get schedule() {
        return this.projects.flatMap((project) =>
            (project.timeline || []).map((event) => ({
                ...event,
                project_name: project.name,
            }))
        ).sort((a, b) => (a.date || "").localeCompare(b.date || ""));
    }
}

registry.category("public_components").add(
    "implementation_hub.PortalApp",
    ImplementationHubPortal
);
