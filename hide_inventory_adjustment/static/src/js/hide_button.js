
odoo.define('hide_inventory_adjustment_button.hide_button', function (require) {
    'use strict';
    const publicWidget = require('web.public.widget');

    publicWidget.registry.HideInventoryButton = publicWidget.Widget.extend({
        selector: '.o_stock_barcode_main_menu',
        start: function () {
            const invBtn = document.querySelector('.button_inventory');
            if (invBtn) {
                invBtn.style.display = 'none';
            }
        }
    });
});
