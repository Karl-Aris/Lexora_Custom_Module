/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.AuthorizeNetFeeNotice = publicWidget.Widget.extend({
    selector: '.o_payment_provider_selector',
    events: {
        'click input[name="o_payment_radio"]': '_onPaymentMethodClick',
    },

    _onPaymentMethodClick: function (ev) {
        const providerId = $(ev.currentTarget).data('provider-id');
        const providerName = $(ev.currentTarget).data('provider-name') || '';
        if (providerName.toLowerCase().includes('authorize.net')) {
            alert("⚠ You will be charged an additional 3.5% fee when paying with Authorize.Net.");
        }
    },
});

export default publicWidget.registry.AuthorizeNetFeeNotice;
