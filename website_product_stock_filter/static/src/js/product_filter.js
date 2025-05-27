odoo.define('website_product_stock_filter.product_filter', function (require) {
    const publicWidget = require('web.public.widget');

    publicWidget.registry.ProductStockFilter = publicWidget.Widget.extend({
        selector: '.availability-checkbox',
        events: {
            'change': '_onAvailabilityChange',
        },

        _onAvailabilityChange: function () {
            const selected = [];
            document.querySelectorAll('.availability-checkbox:checked').forEach(el => {
                selected.push(el.value);
            });
            const url = new URL(window.location);
            url.searchParams.delete('availability');
            if (selected.length > 0) {
                url.searchParams.set('availability', selected.join(','));
            }
            window.location = url.toString();
        },
    });
});