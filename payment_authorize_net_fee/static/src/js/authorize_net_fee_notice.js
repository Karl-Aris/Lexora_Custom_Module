document.addEventListener('DOMContentLoaded', function () {
    const paymentRadios = document.querySelectorAll('input[name="payment_method"]');

    paymentRadios.forEach(radio => {
        radio.addEventListener('change', function () {
            if (this.value === 'authorize_net') {
                alert('You will be charged an additional 3.5% fee for payments made via Authorize.Net.');
            }
        });
    });
});
