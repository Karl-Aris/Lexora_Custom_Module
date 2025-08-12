/** @odoo-module **/

import { onMounted, ref } from "@odoo/owl";

class PaymentAuthorizeNet {
    constructor() {
        this.payButton = null;
        this.radioButtons = [];
        this.selectedProviderCode = ref(null);

        onMounted(() => {
            this.payButton = document.querySelector('button[name="o_payment_submit_button"]');
            this.radioButtons = [...document.querySelectorAll('input[name="o_payment_radio"]')];
            this._bindEvents();
            this._togglePayButton();
        });
    }

    _bindEvents() {
        this.radioButtons.forEach(rb => {
            rb.addEventListener('change', () => {
                this.selectedProviderCode.value = rb.dataset.provider_code;
                this._togglePayButton();
            });
        });

        if (this.payButton) {
            this.payButton.addEventListener('click', (ev) => {
                if (this.selectedProviderCode.value === 'authorize') {
                    ev.preventDefault();
                    if (confirm("Paying via Authorize.Net will add a 3.5% processing fee to your total. Do you wish to continue?")) {
                        this.payButton.closest('form').submit();
                    }
                }
            });
        }
    }

    _togglePayButton() {
        const checked = this.radioButtons.some(rb => rb.checked);
        if (this.payButton) {
            this.payButton.disabled = !checked;
        }
    }
}

new PaymentAuthorizeNet();
