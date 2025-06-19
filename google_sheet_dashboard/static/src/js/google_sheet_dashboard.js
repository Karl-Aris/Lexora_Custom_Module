odoo.define('google_sheet_dashboard.google_sheet_dashboard', ['web.AbstractAction', 'web.core'], function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');

    var GoogleSheetDashboard = AbstractAction.extend({
        template: 'google_sheet_iframe',
    });

    core.action_registry.add('google_sheet_dashboard', GoogleSheetDashboard);

    return GoogleSheetDashboard;
});
