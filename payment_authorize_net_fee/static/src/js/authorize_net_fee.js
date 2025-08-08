/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonRpc } from "@web/core/network/rpc_service";

publicWidget.registry.AuthorizeNetFeeHandler = publicWidget.Widget.extend({
    selector: 'form.o_payment_form',
    events: {
        'change input[name="payment_method_id"]': '_onPaymentMethodChange',
    },

    _onPaymentMethodChange: function (ev) {
        const selectedId = $(ev.currentTarget).val();
        const $form = this.$el;

        // Get provider code from data attribute (set by Odoo)
        const providerCode = $form.find(`input[name="payment_method_id"][value="${selectedId}"]`).data('provider_code');

        // Only trigger for Authorize.Net
        if (providerCode === 'authorize_net') {
            const saleOrderId = parseInt($form.data('sale-order-id'));
            if (!saleOrderId) return;

            jsonRpc("/authorize_net/add_fee", 'call', { sale_order_id: saleOrderId })
                .then((res) => {
                    if (res.success) {
                        console.log(`Authorize.Net fee added. New total: ${res.new_total}`);
                        // Refresh page to update total before payment
                        window.location.reload();
                    } else {
                        console.warn("Authorize.Net fee error:", res.error);
                    }
                });
        }
    },
});

export default publicWidget.registry.AuthorizeNetFeeHandler;
