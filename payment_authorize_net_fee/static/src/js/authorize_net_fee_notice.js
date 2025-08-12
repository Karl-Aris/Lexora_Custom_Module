odoo.define('payment_authorize_net_fee.notice', function (require) {
    'use strict';

    const publicWidget = require('web.public.widget');

    publicWidget.registry.AuthorizeNetFeeNotice = publicWidget.Widget.extend({
        selector: 'form.o_payment_form', // Payment form on website
        events: {
            'change input[name="pm_id"]': '_onPaymentMethodChange',
        },

        _onPaymentMethodChange: function (ev) {
            const $input = $(ev.currentTarget);
            const methodName = $input.closest('.o_payment_acquirer').find('.o_payment_acquirer_name').text().trim();

            // Adjust to match your Authorize.Net name or data attribute
            if (methodName.includes('Authorize.Net')) {
                if (!confirm("By selecting Authorize.Net, a 3.5% processing fee will be added to your order total. Do you wish to continue?")) {
                    // If they click Cancel, unselect Authorize.Net
                    $input.prop('checked', false);
                }
            }
        },
    });

    return publicWidget.registry.AuthorizeNetFeeNotice;
});
