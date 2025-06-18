/** @odoo-module **/

import { registry } from "@web/core/registry";
import AbstractAction from "@web/webclient/actions/abstract_action";

export class GoogleSheetDashboard extends AbstractAction {
    setup() {
        // Any additional logic if needed
    }

    async willStart() {
        await super.willStart();
    }
}

GoogleSheetDashboard.template = "google_sheet_dashboard.google_sheet_iframe";

// Register the action
registry.category("actions").add("google_sheet_dashboard.action", GoogleSheetDashboard);
