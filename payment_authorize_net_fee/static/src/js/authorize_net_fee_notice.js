/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PaymentForm } from "@payment/js/payment_form";
import { Dialog } from "@web/core/dialog/dialog";

patch(PaymentForm.prototype, "authorize_net_fee_notice", {
    async pay(ev) {
        const selectedProvider = this.paymentProviderId;
        if (selectedProvider && this.paymentProviderCode === "authorize") { // <-- must match your provider code
            ev.preventDefault();
            ev.stopPropagation();

            const confirmed = await new Promise((resolve) => {
                this.dialogService.add(Dialog, {
                    title: "Payment Fee Notice",
                    body: "You will be charged an additional 3.5% fee for payments made via Authorize.Net. Do you want to continue?",
                    buttons: [
                        { text: "Cancel", close: true, click: () => resolve(false) },
                        { text: "Continue", primary: true, close: true, click: () => resolve(true) },
                    ],
                });
            });

            if (!confirmed) {
                return;
            }
        }
        return await super.pay(ev);
    },
});
