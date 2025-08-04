/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

console.log("Authorize.Net fee script loaded");

publicWidget.registry.AuthorizeNetFee = publicWidget.Widget.extend({
    selector: '.payment_options',
    events: {
        'change input[name="o_payment_provider_id"]': '_onPaymentProviderChange',
    },

    start() {
        this._onPaymentProviderChange();  // Initial check on load
        return this._super(...arguments);
    },

    _onPaymentProviderChange() {
        const selectedProvider = this.$('input[name="o_payment_provider_id"]:checked').data('provider');

        if (selectedProvider === 'authorize') {
            console.log("Authorize.Net selected - 3.5% fee will apply");

            // OPTIONAL: Display a visual notice
            if ($('#authorize_fee_notice').length === 0) {
                this.$el.append(`
                    <div id="authorize_fee_notice" class="alert alert-warning mt-2">
                        A 3.5% Authorize.Net fee will be added at confirmation.
                    </div>
                `);
            }

        } else {
            console.log("Other payment provider selected");

            // Remove the notice if it exists
            $('#authorize_fee_notice').remove();
        }
    }
});
