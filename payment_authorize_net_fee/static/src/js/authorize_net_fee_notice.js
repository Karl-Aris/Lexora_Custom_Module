/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.AuthorizeNetFeeNotice = publicWidget.Widget.extend({
    selector: '#o_payment_form',

    start: function () {
        this.el.addEventListener('submit', (ev) => {
            const selectedOption = this.el.querySelector('input[name="pm_id"]:checked');
            if (selectedOption && selectedOption.dataset.provider === 'authorize') {
                if (!confirm("⚠ You will be charged an additional 3.5% fee for payments made via Authorize.Net.\n\nDo you want to continue?")) {
                    ev.preventDefault();
                    ev.stopPropagation();
                    return false;
                }
            }
        });
        return this._super.apply(this, arguments);
    },
});
