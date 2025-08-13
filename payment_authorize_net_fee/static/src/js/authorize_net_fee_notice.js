/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.AuthorizeNetFeeNotice = publicWidget.Widget.extend({
    selector: '.o_payment_methods',  // container for all payment methods
    events: {
        'click .o_payment_method': '_onPaymentMethodClick',
    },

    _onPaymentMethodClick: function (ev) {
        const methodCard = ev.currentTarget;
        const providerCode = methodCard.getAttribute('data-provider');  // Odoo sets this
        if (providerCode && providerCode.toLowerCase().includes('authorize')) {
            alert('You will be charged an additional 3.5% fee for payments made via Authorize.Net.');
        }
    },
});

export default publicWidget.registry.AuthorizeNetFeeNotice;
