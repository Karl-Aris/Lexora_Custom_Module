/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PaymentForm } from "@payment/js/payment_form";
import { Dialog } from "@web/core/dialog/dialog";

patch(PaymentForm.prototype, "authorize_net_fee_notice", {
    async pay(ev) {
        const selectedProvider = this.paymentProviderId;
        // Replace 'authorize' with your actual payment.provider.code
        if (selectedProvider && this.paymentProviderCode === "authorize") {
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
        // Call the original pay method
        await this._super(ev);
    },
});
