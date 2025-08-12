odoo.define('payment_authorize_net_fee.notice', function (require) {
    'use strict';

    const publicWidget = require('web.public.widget');

    publicWidget.registry.AuthorizeNetFeeNotice = publicWidget.Widget.extend({
        selector: 'form.o_payment_form', // payment form container
        events: {
            'click button[name="o_payment_submit_button"]': '_onPayClick',
        },

        _onPayClick: function (ev) {
            const $selected = this.$('input[name="o_payment_radio"]:checked');
            const providerCode = $selected.data('provider_code');

            if (providerCode === 'authorize_net') {
                ev.preventDefault(); // stop immediate submission

                // Show browser confirm dialog (simplest way)
                if (confirm("Paying via Authorize.Net will add a 3.5% processing fee to your total. Do you wish to continue?")) {
                    this.el.submit(); // proceed with payment
                }
            }
            // else: let default submit happen
        },
    });

    return publicWidget.registry.AuthorizeNetFeeNotice;
});
