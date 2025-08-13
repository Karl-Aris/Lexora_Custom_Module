/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.AuthorizeNetFeeNotice = publicWidget.Widget.extend({
    selector: "#o_payment_methods",
    events: {
        "click li[name='o_payment_option']": "_onPaymentMethodClick",
    },

    init() {
        this._super(...arguments);
        this.seenAuthorizeNetAlert = false;
    },

    _onPaymentMethodClick: function (ev) {
        const methodText = ev.currentTarget.innerText.toLowerCase();
        const isAuthorizeNet = methodText.includes("authorize.net");

        if (isAuthorizeNet && !this.seenAuthorizeNetAlert) {
            this.seenAuthorizeNetAlert = true;
            alert("You will be charged an additional 3.5% fee for payments made via Authorize.Net.");
        }
    },
});

export default publicWidget.registry.AuthorizeNetFeeNotice;
