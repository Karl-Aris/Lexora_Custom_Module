odoo.define('payment_authorize_net_fee.fee_display', function(require) {
    const publicWidget = require('web.public.widget');
    publicWidget.registry.PaymentFees = publicWidget.Widget.extend({
        selector: '.o_payment_acquirer_methods',
        start() {
            this._updateFees();
        },
        _updateFees() {
            document.querySelectorAll('input[name="pm_id"]').forEach(el => {
                el.addEventListener('change', e => {
                    const selected = e.target.closest('label');
                    if (selected && selected.innerText.includes('Authorize.Net')) {
                        const fee = document.createElement('span');
                        fee.classList.add('text-warning');
                        fee.innerText = '+ 3.5% Fees';
                        selected.appendChild(fee);
                    }
                });
            });
        }
    });
});
