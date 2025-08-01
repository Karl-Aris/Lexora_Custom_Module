odoo.define('authorize_net_fee.website_sale', function (require) {
    'use strict';

    const publicWidget = require('web.public.widget');

    publicWidget.registry.PaymentFeeAuthorizeNet = publicWidget.Widget.extend({
        selector: '.o_payment_form',
        events: {
            'change input[name="o_payment_radio"]': '_onPaymentMethodChange',
        },

        _onPaymentMethodChange: function () {
            const $selected = this.$('input[name="o_payment_radio"]:checked');
            const providerName = $selected.closest('.o_payment_provider').data('provider');

            this.$('.o_payment_provider').each(function () {
                const $feeTag = $(this).find('.payment-fee');
                $feeTag.remove();  // Clear all first
            });

            if (providerName === 'authorize') {
                const orderTotal = parseFloat($('.oe_website_sale .oe_currency_value').text().replace(/[^0-9.-]+/g,""));
                const fee = +(orderTotal * 0.035).toFixed(2);
                const $label = $('<div class="payment-fee text-danger">+ $' + fee + ' Fees</div>');
                $selected.closest('.o_payment_provider').append($label);
            }
        },
    });

    return publicWidget.registry.PaymentFeeAuthorizeNet;
});
