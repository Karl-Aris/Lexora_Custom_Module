odoo.define('website_payment_fee_ui.payment_fee', function (require) {
    "use strict";

    const publicWidget = require('web.public.widget');
    const rpc = require('web.rpc');

    publicWidget.registry.PaymentFee = publicWidget.Widget.extend({
        selector: '.o_payment_provider',

        events: {
            'click input[name="provider"]': '_onProviderClick',
        },

        _onProviderClick: function (ev) {
            const provider = ev.currentTarget.value;

            rpc.query({
                route: "/shop/payment",
                params: { provider: provider },
            });
        },
    });

    return publicWidget.registry.PaymentFee;
});
