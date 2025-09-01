/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

const originalSave = FormController.prototype.saveButtonClicked;

patch(FormController.prototype, {
    async saveButtonClicked(params = {}) {
        const dialogService = this.env.services.dialog;

        // 🔎 Log what’s happening
        console.log("DEBUG - resModel:", this.model.config.resModel);
        console.log("DEBUG - available data:", this.model.root?.data);

        // Only apply on helpdesk.ticket
        if (this.model.config.resModel === "helpdesk.ticket") {
            const result = this.model.root?.data?.x_result;
            console.log("DEBUG - x_result value:", result);

            if (result === "Sub Accepted") {
                return new Promise((resolve) => {
                    dialogService.add(ConfirmationDialog, {
                        title: "Confirmation",
                        body: "Are you sure you want to proceed on this substitution?",
                        confirm: async () => {
                            resolve(originalSave.call(this, params));
                        },
                        cancel: () => {
                            resolve(false);
                        },
                    });
                });
            }
        }

        return originalSave.call(this, params);
    },
});
