/** @odoo-module */

import { listView } from "@web/views/list/list_view";
// import { InventoryReportListModel } from "./inventory_report_list_model";
import { SaleOrderImportLexoraController } from "./sale_order_import_button_controller";
import { RelationalModel } from "@web/model/relational_model/relational_model";
import { ListController } from "@web/views/list/list_controller";
import { registry } from "@web/core/registry";

export const SaleOrderImportLexora = {
    ...listView,
    // Model: RelationalModel,
    Controller: SaleOrderImportLexoraController,
    buttonTemplate: 'sale_order_import.Buttons',
};

registry.category("views").add('sale_order_import_lexora', SaleOrderImportLexora);
