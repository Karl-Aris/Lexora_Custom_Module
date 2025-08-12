odoo.define('payment_authorize_net_fee.notice', function (require) {
    'use strict';

    const publicWidget = require('web.public.widget');

    publicWidget.registry.AuthorizeNetFeeNotice = publicWidget.Widget.extend({
        selector: '.o_payment_acquirer_select',
        events: {
            'change input[name="o_payment_radio"]': '_onPaymentMethodChange',
        },
        popupShown: false,  // ensure it only shows once

        _onPaymentMethodChange: function (ev) {
            const $input = $(ev.currentTarget);
            const providerCode = $input.data('provider_code'); // Odoo sets this
            if (providerCode === 'authorize_net' && !this.popupShown) {
                this.popupShown = true;
                this._showPopup();
            }
        },

        _showPopup: function () {
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

    return publicWidget.registry.AuthorizeNetFeeNotice;
});
