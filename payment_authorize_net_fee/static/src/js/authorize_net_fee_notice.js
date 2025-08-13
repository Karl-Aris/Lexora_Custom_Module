/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.AuthorizeNetFeeNotice = publicWidget.Widget.extend({
    selector: '.o_payment_form',

    start: function () {
        const radios = this.el.querySelectorAll('input[name="pm_id"]');
        radios.forEach((radio) => {
            radio.addEventListener('change', (ev) => {
                const selected = ev.target;
                if (selected && selected.dataset.provider === 'authorize') {
                    alert("⚠ You will be charged an additional 3.5% fee for payments made via Authorize.Net.");
                }
            });
        });
        return this._super.apply(this, arguments);
    },
});
