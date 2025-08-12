<t t-javascript="true">
document.addEventListener('DOMContentLoaded', function () {
    // Adjust selector to your payment method radio buttons
    const paymentRadios = document.querySelectorAll('input[name="payment_method"]');

    paymentRadios.forEach(radio => {
        radio.addEventListener('change', function () {
            if (this.value === 'authorize_net') {  // match your payment provider code here
                // Show modal or alert
                if (!document.getElementById('authNetFeeModal')) {
                    const modalHtml = `
                    <div class="modal fade" id="authNetFeeModal" tabindex="-1" aria-labelledby="authNetFeeModalLabel" aria-hidden="true">
                      <div class="modal-dialog">
                        <div class="modal-content">
                          <div class="modal-header">
                            <h5 class="modal-title" id="authNetFeeModalLabel">Authorize.Net Payment Fee</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                          </div>
                          <div class="modal-body">
                            You will be charged an additional 3.5% processing fee for payments made via Authorize.Net.
                          </div>
                          <div class="modal-footer">
                            <button type="button" class="btn btn-primary" data-bs-dismiss="modal">OK</button>
                          </div>
                        </div>
                      </div>
                    </div>
                    `;
                    document.body.insertAdjacentHTML('beforeend', modalHtml);
                }

                const authNetFeeModal = new bootstrap.Modal(document.getElementById('authNetFeeModal'));
                authNetFeeModal.show();
            }
        });
    });
});
</t>
