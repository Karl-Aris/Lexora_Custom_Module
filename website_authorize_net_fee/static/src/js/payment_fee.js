console.log("Authorize.Net payment_fee.js loaded!");

odoo.define('website_authorize_net_fee.payment_fee', function (require) {
    "use strict";

    const publicWidget = require('web.public.widget');

    publicWidget.registry.PaymentFee = publicWidget.Widget.extend({
        selector: '.o_payment_provider',
        start: function () {
            const providers = this.el.querySelectorAll('input[name="o_payment_provider"]');
            providers.forEach((input) => {
                input.addEventListener('change', () => {
                    if (input.value === 'authorize') {
                        console.log("Authorize.Net selected - apply fee logic here");
                        // Implement fee logic if necessary
                    }
                });
            });
        }
    });
});
