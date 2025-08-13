/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import Dialog from "@web/legacy/js/core/dialog";

publicWidget.registry.AuthorizeNetFeeNotice = publicWidget.Widget.extend({
    selector: '.o_payment_form', // Payment form wrapper
    events: {
        'click button[type="submit"]': '_onPayClick',
    },

    _onPayClick: function (ev) {
        const selectedProvider = this.$('input[name="provider"]:checked').val();

        if (selectedProvider === 'authorize') {  // Must match payment.provider.code
            ev.preventDefault(); // stop form from submitting
            ev.stopPropagation();

            // Show nice Odoo popup
            Dialog.confirm(this, 
                "You will be charged an additional 3.5% fee for payments made via Authorize.Net. Do you want to continue?",
                {
                    confirm_callback: () => {
                        this.el.submit(); // proceed after user confirms
                    },
                    title: "Payment Fee Notice",
                }
            );
        }
    },
});

export default publicWidget.registry.AuthorizeNetFeeNotice;
