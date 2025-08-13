/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.AuthorizeNetFeeNotice = publicWidget.Widget.extend({
    selector: 'body', // bind to body so it also works when modal is loaded dynamically

    start: function () {
        // Listen for clicks on any payment method option
        this.el.addEventListener('click', (ev) => {
            const target = ev.target.closest('.o_payment_option_card');
            if (target) {
                // Check if this is the Authorize.Net payment option
                const providerName = target.dataset.provider;
                if (providerName && providerName.toLowerCase().includes('authorize')) {
                    alert("⚠ You will be charged an additional 3.5% fee for payments made via Authorize.Net.");
                }
            }
        });
        return this._super.apply(this, arguments);
    },
});
