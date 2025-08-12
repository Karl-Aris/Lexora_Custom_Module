odoo.define('payment_authorize_net_fee.notice', function (require) {
    'use strict';

    const publicWidget = require('web.public.widget');

    publicWidget.registry.AuthorizeNetFeeNotice = publicWidget.Widget.extend({
        selector: 'form.o_payment_form',  // payment form in checkout & portal
        events: {
            'click input[name="o_payment_radio"]': '_onPaymentMethodClick',
        },

        _onPaymentMethodClick: function (ev) {
            const $option = $(ev.currentTarget);
            const providerCode = $option.data('provider_code');

            // Only trigger for Authorize.Net
            if (providerCode === 'authorize_net' && !sessionStorage.getItem('auth_net_fee_notice_shown')) {
                alert('Notice: A 3.5% processing fee will be added to your payment when using Authorize.Net.');
                sessionStorage.setItem('auth_net_fee_notice_shown', '1');
            }
        },
    });

    return publicWidget.registry.AuthorizeNetFeeNotice;
});
