/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { session } from "@web/session";
import { ListController } from "@web/views/list/list_controller";

export class ReturnReportController extends ListController {
    async openImportOrdersWizard() {
        return this.actionService.doAction("return_report.action_importation_wizard_open", {
        });
    }
    async openImportPlatformsWizard() {
        return this.actionService.doAction("return_report.action_importation_platform_wizard_open", {
        });
    }
}
