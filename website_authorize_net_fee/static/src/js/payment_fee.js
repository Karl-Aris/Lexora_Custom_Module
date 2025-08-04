odoo.define('website_authorize_net_fee.payment_fee', function (require) {
    'use strict';

    const publicWidget = require('web.public.widget');
    const ajax = require('web.ajax');

    publicWidget.registry.PaymentFeeHandler = publicWidget.Widget.extend({
        selector: '.o_payment_provider',

        events: {
            'change input[name="o_payment_provider"]': '_onProviderChange',
        },

        _onProviderChange: function () {
            const selectedProvider = this.$('input[name="o_payment_provider"]:checked').val();
            const isAuthorizeNet = selectedProvider && selectedProvider.includes('authorize');

            ajax.jsonRpc('/update_authnet_fee', 'call', {
                add_fee: isAuthorizeNet
            }).then(function (result) {
                window.location.reload();
            });
        },
    });

    return publicWidget.registry.PaymentFeeHandler;
});
