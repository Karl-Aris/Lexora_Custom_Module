odoo.define('custom_authorize_net_fee.fee_dynamic', function (require) {
    "use strict";

    var publicWidget = require('web.public.widget');
    var ajax = require('web.ajax');

    publicWidget.registry.AuthorizeNetFee = publicWidget.Widget.extend({
        selector: '.o_payment_provider',
        events: {
            'change input[type="radio"]': '_onPaymentMethodChange',
        },

        _onPaymentMethodChange: function (ev) {
            var $input = $(ev.currentTarget);
            if ($input.val().includes('authorize')) {
                ajax.jsonRpc('/shop/payment/authorize_net_fee', 'call', {})
                    .then(function (result) {
                        console.log('Authorize.Net fee applied:', result);
                    });
            }
        },
    });

    return publicWidget.registry.AuthorizeNetFee;
});
