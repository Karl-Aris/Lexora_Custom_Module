odoo.define('your_module.payment_authorize_net', function (require) {
    "use strict";
    var publicWidget = require('web.public.widget');

    publicWidget.registry.PaymentAuthorizeNet = publicWidget.Widget.extend({
        selector: '#payment_form', // or your actual payment form selector
        events: {
            'change input[name="o_payment_radio"]': '_onPaymentMethodChange',
            'click button[name="o_payment_submit_button"]': '_onPayClick',
        },
        start: function () {
            this._togglePayButton();
            return this._super.apply(this, arguments);
        },
        _togglePayButton: function () {
            var checked = this.$('input[name="o_payment_radio"]:checked').length > 0;
            this.$('button[name="o_payment_submit_button"]').prop('disabled', !checked);
        },
        _onPaymentMethodChange: function () {
            this._togglePayButton();
        },
        _onPayClick: function (ev) {
            var provider = this.$('input[name="o_payment_radio"]:checked').data('provider_code');
            if (provider === 'authorize') {
                ev.preventDefault();
                if (confirm("Paying via Authorize.Net will add a 3.5% processing fee to your total. Do you wish to continue?")) {
                    this.$('form').submit();
                }
            }
        },
    });
});
