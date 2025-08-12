odoo.define('payment_authorize_net_fee.notice', function (require) {
    'use strict';

    const PaymentForm = require('payment.payment_form');

    PaymentForm.include({
        events: Object.assign({}, PaymentForm.prototype.events, {
            'change input[name="o_payment_radio"]': '_onPaymentMethodChangeWithNotice',
        }),

        _onPaymentMethodChangeWithNotice: function (ev) {
            this._super.apply(this, arguments); // keep Odoo's normal behavior

            const $input = $(ev.currentTarget);
            const providerCode = $input.data('provider_code'); // Odoo sets this in payment template
            if (providerCode === 'authorize_net' && !this.authorizeNetPopupShown) {
                this.authorizeNetPopupShown = true;
                this._showAuthorizeNetNotice();
            }
        },

        _showAuthorizeNetNotice: function () {
            const $modal = $(`
                <div class="modal fade" tabindex="-1" role="dialog">
                  <div class="modal-dialog modal-dialog-centered" role="document">
                    <div class="modal-content">
                      <div class="modal-header">
                        <h5 class="modal-title">Authorize.Net Payment Notice</h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                          <span aria-hidden="true">&times;</span>
                        </button>
                      </div>
                      <div class="modal-body">
                        <p>Paying via Authorize.Net will add a <strong>3.5% processing fee</strong> to your order total.</p>
                      </div>
                      <div class="modal-footer">
                        <button type="button" class="btn btn-primary" data-dismiss="modal">OK</button>
                      </div>
                    </div>
                  </div>
                </div>
            `);
            $modal.appendTo('body').modal('show');
        },
    });

    return PaymentForm;
});
