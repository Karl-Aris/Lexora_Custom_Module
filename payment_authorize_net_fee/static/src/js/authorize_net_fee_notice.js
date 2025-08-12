/** @odoo-module **/

document.addEventListener('DOMContentLoaded', () => {
    const payButton = document.querySelector('button[name="o_payment_submit_button"]');
    if (!payButton) {
        console.error('Pay button not found');
        return;
    }

    const paymentRadios = Array.from(document.querySelectorAll('input[name="o_payment_radio"]'));
    if (paymentRadios.length === 0) {
        console.error('Payment radio buttons not found');
        return;
    }

    function isAuthorizeSelected() {
        return paymentRadios.some(radio => radio.checked && radio.dataset.providerCode === 'authorize');
    }

    function togglePayButton() {
        payButton.disabled = !paymentRadios.some(radio => radio.checked);
    }

    paymentRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            togglePayButton();
        });
    });

    togglePayButton();

    payButton.addEventListener('click', (ev) => {
        if (isAuthorizeSelected()) {
            ev.preventDefault();
            if (confirm("A 3.5% processing fee will be added for Authorize.Net. Proceed?")) {
                payButton.closest('form').submit();
            }
        }
    });
});
