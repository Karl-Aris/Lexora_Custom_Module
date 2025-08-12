odoo.define('payment_authorize_net_fee.notice', function (require) {
    'use strict';

    const publicWidget = require('web.public.widget');

    publicWidget.registry.AuthorizeNetFeeNotice = publicWidget.Widget.extend({
        selector: 'body', // global
        start: function () {
            this._watchForPaymentForms();
            return this._super(...arguments);
        },

        _watchForPaymentForms: function () {
            const observer = new MutationObserver(() => {
                document.querySelectorAll('.o_payment_form').forEach(form => {
                    this._bindFeeNotice(form);
                });
            });
            observer.observe(document.body, { childList: true, subtree: true });
        },

        _bindFeeNotice: function (form) {
            if (form.dataset.authorizeNetFeeBound) return;
            form.dataset.authorizeNetFeeBound = "true";

            const submitBtn = form.querySelector('button[type="submit"]');
            if (!submitBtn) return;

            submitBtn.addEventListener('click', (ev) => {
                const selected = form.querySelector('input[name="pm_id"]:checked');
                if (!selected) return;

                const methodName = selected.closest('.o_payment_acquirer')?.querySelector('.o_payment_acquirer_name')?.textContent?.trim().toLowerCase() || '';
                if (methodName.includes('authorize.net')) {
                    // Stop *only once* to show modal, not in subsequent confirmation
                    if (!form.dataset.feeNoticeConfirmed) {
                        ev.stopPropagation();
                        ev.preventDefault();
                        this._showModal(() => {
                            form.dataset.feeNoticeConfirmed = "true";
                            submitBtn.click(); // retry submit
                        });
                    }
                }
            }, true); // capture phase so Odoo's own click handler still runs after ours if we allow
        },

        _showModal: function (onConfirm) {
            if (!document.getElementById('authorizeNetFeeModal')) {
                document.body.insertAdjacentHTML('beforeend', `
                    <div class="modal fade" id="authorizeNetFeeModal" tabindex="-1" role="dialog">
                      <div class="modal-dialog modal-dialog-centered" role="document">
                        <div class="modal-content">
                          <div class="modal-header">
                            <h5 class="modal-title">Authorize.Net Processing Fee</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                          </div>
                          <div class="modal-body">
                            <p>By selecting Authorize.Net, a <strong>3.5% processing fee</strong> will be added to your order total.</p>
                            <p>Do you want to continue?</p>
                          </div>
                          <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" id="authorizeNetFeeConfirm">Yes, Continue</button>
                          </div>
                        </div>
                      </div>
                    </div>
                `);
            }

            const modal = new bootstrap.Modal(document.getElementById('authorizeNetFeeModal'));
            modal.show();

            document.getElementById('authorizeNetFeeConfirm').onclick = () => {
                modal.hide();
                onConfirm();
            };
        },
    });

    return publicWidget.registry.AuthorizeNetFeeNotice;
});
