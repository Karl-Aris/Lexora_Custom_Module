odoo.define('website_payment_fee.payment_fee', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.PaymentFee = publicWidget.Widget.extend({
        selector: '.o_payment',
        events: {
            'change input[name="provider_id"]': '_onPaymentMethodChange',
        },

        _onPaymentMethodChange: function (ev) {
            var providerId = $(ev.currentTarget).val();
            if (!providerId) return;

            $.get('/payment/get_fee', { provider_id: providerId }).then(function (data) {
                $('label[for="provider_' + providerId + '"]').find('.payment-fee-amount').remove();
                $('label[for="provider_' + providerId + '"]').append(
                    '<span class="badge bg-warning text-dark ms-2 payment-fee-amount">' + data.fee_display + '</span>'
                );
            });
        },
    });

    return publicWidget.registry.PaymentFee;
});