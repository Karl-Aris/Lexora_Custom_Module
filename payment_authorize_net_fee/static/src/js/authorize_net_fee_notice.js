/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.AuthorizeNetFeeNotice = publicWidget.Widget.extend({
    selector: '.o_payment_form', // Payment form container
    events: {
        'click button[type="submit"]': '_onSubmit',
    },

    _onSubmit: function (ev) {
        const selectedMethod = this.$('input[name="pm_id"]:checked');
        if (!selectedMethod.length) {
            return; // No payment method selected
        }

        const providerCode = selectedMethod.data('provider');
        if (providerCode === 'authorize') {
            ev.preventDefault();
            if (confirm("⚠ You will be charged an additional 3.5% fee for payments made via Authorize.Net.\n\nDo you wish to continue?")) {
                // If user clicks OK, submit form
                this.el.submit();
            }
        }
    },
});
