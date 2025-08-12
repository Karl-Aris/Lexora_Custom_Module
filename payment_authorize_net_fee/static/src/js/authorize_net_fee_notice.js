odoo.define('payment_authorize_net_fee.portal_notice', function (require) {
    'use strict';
    const publicWidget = require('web.public.widget');

    publicWidget.registry.AuthorizeNetFeeNotice = publicWidget.Widget.extend({
        selector: 'body',
        start: function () {
            this._observer = null;
            this._observePaymentAreas();
            return this._super.apply(this, arguments);
        },

        _observePaymentAreas: function () {
            const self = this;
            // Watch for payment forms / provider lists injected into the DOM
            this._observer = new MutationObserver(function () {
                // forms may be .o_payment_form; provider selection area sometimes has id payment_method or class o_payment_provider_selection
                document.querySelectorAll('.o_payment_form, .o_payment_provider_selection, #payment_method').forEach(function (el) {
                    self._bindContainer($(el));
                });
            });
            this._observer.observe(document.body, { childList: true, subtree: true });

            // initial pass
            document.querySelectorAll('.o_payment_form, .o_payment_provider_selection, #payment_method').forEach(function (el) {
                this._bindContainer($(el));
            }.bind(this));
        },

        _bindContainer: function ($ctx) {
            // avoid double-binding
            if ($ctx.data('authNetBound')) {
                return;
            }
            $ctx.data('authNetBound', true);

            // ensure a notice exists somewhere near the payment area (we inserted it server-side but fallback here)
            let $notice = $ctx.closest('#modalaccept').find('#authorize_fee_notice');
            if (!$notice.length) {
                // fallback: prepend inside this context
                const fallback = `
                  <div id="authorize_fee_notice" class="alert alert-warning d-none" role="alert" style="margin-bottom:1rem;">
                    <p class="mb-2">
                      By selecting <strong>Authorize.Net</strong>, a <strong>3.5% processing fee</strong> will be added to your order total.
                    </p>
                    <div class="form-check">
                      <input class="form-check-input" type="checkbox" id="authorize_fee_confirm" name="authorize_fee_confirm"/>
                      <label class="form-check-label" for="authorize_fee_confirm">I accept the 3.5% Authorize.Net processing fee.</label>
                    </div>
                  </div>`;
                $ctx.prepend(fallback);
                $notice = $ctx.find('#authorize_fee_notice');
            }

            const $checkbox = $notice.find('#authorize_fee_confirm');

            // find submit buttons relevant to this payment form/modal (visible ones)
            const findSubmitButtons = function () {
                // try to find buttons within the same modal/form
                const $modal = $ctx.closest('.modal');
                let $buttons = $ctx.find('button[type="submit"], button.js_pay_button, button.o_pay_button').filter(':visible');
                if (!$buttons.length && $modal.length) {
                    $buttons = $modal.find('button[type="submit"], button.js_pay_button, button.o_pay_button').filter(':visible');
                }
                return $buttons;
            };

            // On provider radio change => show/hide notice and enable/disable submit
            const radioSelector = 'input[name="provider_id"], input[name="pm_id"], input[name="acquirer_id"], input[type="radio"].o_payment_radio';
            $ctx.on('change', radioSelector, function (ev) {
                const $input = $(ev.currentTarget);

                // try data attributes first
                let providerName = ($input.data('provider-name') || $input.data('provider_name') || $input.data('provider') || '').toString().trim().toLowerCase();

                // fallback: label text
                if (!providerName) {
                    const $label = $input.closest('label');
                    if ($label.length) {
                        providerName = $label.text().trim().toLowerCase();
                    } else {
                        // fallback: text inside nearest .o_payment_acquirer element
                        const $acquirer = $input.closest('.o_payment_acquirer, .payment-method');
                        if ($acquirer.length) {
                            providerName = $acquirer.text().trim().toLowerCase();
                        }
                    }
                }

                const isAuthorize = providerName && providerName.indexOf('authorize') !== -1;

                const $submitButtons = findSubmitButtons();

                if (isAuthorize) {
                    // show notice, uncheck checkbox, disable submit until checked
                    $notice.removeClass('d-none');
                    $checkbox.prop('checked', false);
                    $submitButtons.prop('disabled', true).addClass('disabled');
                } else {
                    // hide notice and enable submit
                    $notice.addClass('d-none');
                    $submitButtons.prop('disabled', false).removeClass('disabled');
                }
            });

            // On checkbox change => toggle submit enabled
            $ctx.on('change', '#authorize_fee_confirm', function (ev) {
                const checked = $(ev.currentTarget).is(':checked');
                const $submitButtons = findSubmitButtons();
                if (checked) {
                    $submitButtons.prop('disabled', false).removeClass('disabled');
                } else {
                    $submitButtons.prop('disabled', true).addClass('disabled');
                }
            });

            // If a provider is already pre-selected on load, trigger a change to initialize notice state
            $ctx.find(radioSelector + ':checked').each(function () {
                $(this).trigger('change');
            });
        }
    });

    return publicWidget.registry.AuthorizeNetFeeNotice;
});
