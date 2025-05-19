odoo.define('custom_authorize_fee.payment_fee', function (require) {
    'use strict';

    const publicWidget = require('web.public.widget');

    publicWidget.registry.PaymentFee = publicWidget.Widget.extend({
        selector: '.o_payment',
        events: {
            'change input[name="o_payment_radio"]': '_onPaymentChange',
        },

        _onPaymentChange: function () {
            const selected = document.querySelector('input[name="o_payment_radio"]:checked');
            const authorizeNet = selected && selected.value.toLowerCase().includes('authorize');

            const totalElement = document.querySelector('#order_total_amount');
            const baseTotal = parseFloat(totalElement.dataset.total);

            let surcharge = 0;
            if (authorizeNet) surcharge = +(baseTotal * 0.03).toFixed(2);

            const feeRow = document.getElementById('payment_fee_line');
            if (feeRow) feeRow.remove();

            if (surcharge > 0) {
                const row = document.createElement('tr');
                row.id = "payment_fee_line";
                row.innerHTML = `<td>Authorize.Net Fee</td><td>$${surcharge}</td>`;
                totalElement.closest('table').insertBefore(row, totalElement.closest('tr'));
                document.getElementById('order_total').textContent = `$${(baseTotal + surcharge).toFixed(2)}`;
            } else {
                document.getElementById('order_total').textContent = `$${baseTotal.toFixed(2)}`;
            }
        }
    });
});
