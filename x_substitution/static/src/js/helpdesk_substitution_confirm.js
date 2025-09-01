/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { useService } from "@web/core/utils/hooks";

// Use patch to wrap the method with access to the original
patch(FormController.prototype, {
    saveButtonClicked: function (original, params = {}) {
        // Only apply on helpdesk.ticket
        if (this.model.root.resModel === "helpdesk.ticket") {
            const result = this.model.root.data.x_result;

            if (result === "Sub Accepted") {
                const dialogService = useService("dialog");

                return new Promise((resolve) => {
                    dialogService.add(ConfirmationDialog, {
                        title: "Confirmation",
                        body: "Are you sure you want to proceed on this substitution?",
                        confirm: async () => {
                            resolve(original.call(this, params));  // ✅ safe call
                        },
                        cancel: () => {
                            resolve(false);
                        },
                    });
                });
            }
        }

        // fallback → call original directly
        return original.call(this, params);
    },
});
