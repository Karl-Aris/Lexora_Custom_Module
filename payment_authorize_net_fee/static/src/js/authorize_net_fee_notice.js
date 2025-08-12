odoo.define('payment_authorize_net_fee.notice', function (require) {
    'use strict';

    const publicWidget = require('web.public.widget');

    publicWidget.registry.AuthorizeNetFeeNotice = publicWidget.Widget.extend({
        selector: 'form.o_payment_form',
        events: {
            'click button[type="submit"]': '_onPayNowClick',
        },

        _onPayNowClick: function (ev) {
            const $selected = this.$el.find('input[name="pm_id"]:checked').closest('.o_payment_acquirer');
            const methodName = $selected.find('.o_payment_acquirer_name').text().trim();

            if (methodName && methodName.toLowerCase().includes('authorize.net')) {
                ev.preventDefault(); // Stop the form submit now
                this._showFeeModal(ev.currentTarget);
            }
        },

        _showFeeModal: function (submitButton) {
            const modalHtml = `
                <div class="modal fade" id="authorizeNetFeeModal" tabindex="-1" role="dialog">
                  <div class="modal-dialog modal-dialog-centered" role="document">
                    <div class="modal-content">
                      <div class="modal-header">
                        <h5 class="modal-title">Authorize.Net Processing Fee</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                      </div>
                      <div class="modal-body">
                        <p>By selecting Authorize.Net, a <strong>3.5% processing fee</strong> will be added to your order total.</p>
                        <p>Do you want to continue with Authorize.Net?</p>
                      </div>
                      <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="authorizeNetFeeConfirm">Yes, Continue</button>
                      </div>
                    </div>
                  </div>
                </div>
            `;

            // Append modal to body if not already present
            if (!$('#authorizeNetFeeModal').length) {
                $('body').append(modalHtml);
            }

            const modal = new bootstrap.Modal(document.getElementById('authorizeNetFeeModal'));
            modal.show();

            $('#authorizeNetFeeConfirm').off('click').on('click', () => {
                modal.hide();
                submitButton.click(); // Trigger the original Pay Now click again
            });
        },
    });

    return publicWidget.registry.AuthorizeNetFeeNotice;
});
