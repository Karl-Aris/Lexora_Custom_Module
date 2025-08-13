/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.AuthorizeNetFeeNotice = publicWidget.Widget.extend({
    selector: '.o_payment_form', // This is the payment form container
    events: {
        'change input[name="provider"]': '_onProviderChange',
    },

    _onProviderChange: function (ev) {
        const selectedValue = ev.currentTarget.value;
        if (selectedValue === 'authorize') { // must match your provider_id.code
            alert('You will be charged an additional 3.5% fee for payments made via Authorize.Net.');
        }
    },
});

export default publicWidget.registry.AuthorizeNetFeeNotice;
