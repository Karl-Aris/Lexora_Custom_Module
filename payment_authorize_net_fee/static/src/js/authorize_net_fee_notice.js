/** @odoo-module **/

document.addEventListener('DOMContentLoaded', () => {
    const payButton = document.querySelector('button[name="o_payment_submit_button"]');
    const paymentRadios = [...document.querySelectorAll('input[name="o_payment_radio"]')];

    function isAuthorizeSelected() {
        return paymentRadios.some(radio => radio.checked && radio.dataset.providerCode === 'authorize');
    }

    // Enable/disable Pay button depending on payment selection
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
