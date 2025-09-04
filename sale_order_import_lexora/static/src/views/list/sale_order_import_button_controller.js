/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { session } from "@web/session";
import { ListController } from "@web/views/list/list_controller";

export class SaleOrderImportLexoraController extends ListController {
    async openImportOrdersWizard() {
        return this.actionService.doAction("sale_order_import_lexora.action_importation_wizard_open", {
        });
    }
    async openImportPlatformsWizard() {
        return this.actionService.doAction("sale_order_import_lexora.action_importation_platform_wizard_open", {
        });
    }
}
