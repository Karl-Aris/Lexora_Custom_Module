odoo.define('website_payment_fee_ui.payment_fee', function (require) {
    const publicWidget = require('web.public.widget');

    publicWidget.registry.PaymentFeeDisplay = publicWidget.Widget.extend({
        selector: '.payment_option',
        start: function () {
            this.updateFees();
        },
        updateFees: function () {
            document.querySelectorAll('.payment_option input').forEach(input => {
                input.addEventListener('change', async () => {
                    const providerId = input.value;
                    const resp = await fetch('/get_payment_fee?provider_id=' + providerId);
                    const data = await resp.json();
                    const feeDisplay = input.closest('.payment_option').querySelector('.payment_fee_display');
                    if (feeDisplay) {
                        feeDisplay.innerText = data.fee > 0 ? `+ $${data.fee.toFixed(2)} Fees` : '+ $0.00 Fees';
                    }
                });
            });
        }
    });
});