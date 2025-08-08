/** 
 * Simple JS module to detect payment method change on Odoo website sale payment step
 */
odoo.define('payment_authorize_net_fee_pre.authorize_net_fee', function (require) {
    "use strict";

    var publicWidget = require('web.public.widget');

    publicWidget.registry.AuthorizeNetFee = publicWidget.Widget.extend({
        selector: '.o_payment_form',  // adjust selector to the payment form container
        start: function () {
            var self = this;
            this._super.apply(this, arguments);

            // Listen for changes on payment method radio buttons
            this.$el.on('change', 'input[name="payment_method_id"]', function () {
                var selectedMethodCode = $(this).data('provider'); // usually data-provider has the code
                if (selectedMethodCode === 'authorize') {
                    console.log('Authorize.Net payment method selected');

                    // You can trigger a reload or AJAX call here to update surcharge
                    // For example, trigger a custom event
                    self.trigger_up('payment_method_authorize_selected');
                } else {
                    console.log('Another payment method selected');
                    self.trigger_up('payment_method_authorize_deselected');
                }
            });

            return Promise.resolve();
        },
    });

});
