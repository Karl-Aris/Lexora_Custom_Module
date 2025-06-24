odoo.define('hide_inventory_adjustment_button.hide_button', function (require) {
    "use strict";

    var config = require('web.config');

    if (!config.device.isMobile) {
        document.addEventListener('DOMContentLoaded', function () {
            var observer = new MutationObserver(function () {
                document.querySelectorAll('button[name="action_open_inventory"]').forEach(btn => {
                    btn.style.display = 'none';
                });
            });
            observer.observe(document.body, { childList: true, subtree: true });
        });
    }
});
