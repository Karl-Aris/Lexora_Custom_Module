/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.AuthorizeNetFeeNotice = publicWidget.Widget.extend({
    selector: 'form[name="o_payment_form"]',
    events: {
        'change input[name="payment_method_id"]': '_onPaymentMethodChange',
    },

    _onPaymentMethodChange: function (ev) {
        const selected = this.$(ev.currentTarget);
        // Adjust the data-code or value depending on your payment method DOM
        if (selected.data('provider') === 'authorize') {
            alert('You will be charged an additional 3.5% fee for payments made via Authorize.Net.');
        }
    },
});

export default publicWidget.registry.AuthorizeNetFeeNotice;
