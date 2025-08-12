odoo.define('payment_authorize_net_fee.notice', function (require) {
    'use strict';

    const publicWidget = require('web.public.widget');

    publicWidget.registry.AuthorizeNetFeeNotice = publicWidget.Widget.extend({
        selector: '.o_portal_sign_payment', // Payment form container after signing
        events: {},

        start: function () {
            // Wait for payment form to be injected after signature
            this._observePaymentForm();
            return this._super.apply(this, arguments);
        },

        _observePaymentForm: function () {
            const targetNode = document.querySelector('.o_portal_sign_payment');
            if (!targetNode) return;

            const observer = new MutationObserver(() => {
                const $form = this.$('.o_payment_form');
                if ($form.length) {
                    this._attachHandler($form);
                }
            });

            observer.observe(targetNode, { childList: true, subtree: true });
        },

        _attachHandler: function ($form) {
            if ($form.data('authorizeNetFeeBound')) return; // Avoid double-binding
            $form.data('authorizeNetFeeBound', true);

            $form.find('button[type="submit"]').on('click', (ev) => {
                const $selected = $form.find('input[name="pm_id"]:checked').closest('.o_payment_acquirer');
                const methodName = $selected.find('.o_payment_acquirer_name').text().trim();

                if (methodName && methodName.toLowerCase().includes('authorize.net')) {
                    ev.preventDefault();
                    this._showFeeModal(ev.currentTarget);
                }
            });
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

            if (!$('#authorizeNetFeeModal').length) {
                $('body').append(modalHtml);
            }

            const modal = new bootstrap.Modal(document.getElementById('authorizeNetFeeModal'));
            modal.show();

            $('#authorizeNetFeeConfirm').off('click').on('click', () => {
                modal.hide();
                submitButton.click(); // Resume original payment
            });
        },
    });

    return publicWidget.registry.AuthorizeNetFeeNotice;
});
