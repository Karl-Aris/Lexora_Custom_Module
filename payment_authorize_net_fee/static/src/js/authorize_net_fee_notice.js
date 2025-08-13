/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.AuthorizeNetFeeNotice = publicWidget.Widget.extend({
    selector: "#o_payment_methods",
    events: {
        "click li[name='o_payment_option']": "_onPaymentMethodClick",
    },

    init() {
        this._super(...arguments);
        this.seenAuthorizeNetAlert = false; // Prevent multiple alerts
        this.selectedPaymentId = null; // Track selected method
    },

    _onPaymentMethodClick: function (ev) {
        const methodText = ev.currentTarget.innerText.toLowerCase();
        const isAuthorizeNet = methodText.includes("authorize.net");

        // Find currently selected payment method
        const currentSelected = document.querySelector("li[name='o_payment_option'].o_selected");
        const currentSelectedId = currentSelected ? currentSelected.dataset.id : null;

        // Show alert only if:
        // 1) It's Authorize.Net
        // 2) It's a new selection
        // 3) User hasn't already seen it this session
        if (isAuthorizeNet && currentSelectedId !== this.selectedPaymentId && !this.seenAuthorizeNetAlert) {
            this.seenAuthorizeNetAlert = true;
            this.selectedPaymentId = currentSelectedId;
            alert("You will be charged an additional 3.5% fee for payments made via Authorize.Net.");
        }
    },
});

export default publicWidget.registry.AuthorizeNetFeeNotice;
