/** @odoo-module **/

import { registry } from "@web/core/registry";
import AbstractAction from "@web/webclient/actions/abstract_action";

export class GoogleSheetDashboard extends AbstractAction {}

GoogleSheetDashboard.template = "google_sheet_dashboard.google_sheet_iframe";

registry.category("actions").add("google_sheet_dashboard.action", GoogleSheetDashboard);
