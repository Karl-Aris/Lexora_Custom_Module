/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.AuthorizeNetFeeNotice = publicWidget.Widget.extend({
    selector: "#o_payment_methods",
    events: {
        "click li[name='o_payment_option']": "_onPaymentMethodClick",
    },

    _onPaymentMethodClick: function (ev) {
        const methodText = ev.currentTarget.innerText.toLowerCase();
        if (methodText.includes("authorize.net")) {
            alert("You will be charged an additional 3.5% fee for payments made via Authorize.Net.");
        }
    },
});

export default publicWidget.registry.AuthorizeNetFeeNotice;
