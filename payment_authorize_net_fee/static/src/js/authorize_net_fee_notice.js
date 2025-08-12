odoo.define('payment_authorize_net_fee.notice', function (require) {
    "use strict";

    const publicWidget = require('web.public.widget');
    const Dialog = require('web.Dialog');

    publicWidget.registry.AuthorizeNetFeeNotice = publicWidget.Widget.extend({
        selector: '.o_payment_provider_selection',
        events: {
            'click input[name="provider_id"]': '_onPaymentMethodClick',
        },

        /**
         * Triggered when a payment provider is selected.
         */
        _onPaymentMethodClick: function (ev) {
            const $input = $(ev.currentTarget);
            const providerName = ($input.data('provider-name') || '').toLowerCase();

            // Check if selected method is Authorize.Net
            if (providerName.includes('authorize.net')) {
                Dialog.alert(this, _t("Notice"), {
                    title: _t("Additional Fee"),
                    $content: $("<div/>", {
                        text: "A 3.5% processing fee will be added to your total if you pay using Authorize.Net."
                    }),
                    buttons: [{ text: _t("OK"), close: true }],
                });
            }
        },
    });

    return publicWidget.registry.AuthorizeNetFeeNotice;
});
