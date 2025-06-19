odoo.define('google_sheet_dashboard.google_sheet_dashboard', function (require) {
    'use strict';

    const AbstractAction = require('web.AbstractAction');
    const core = require('web.core');

    const GoogleSheetDashboard = AbstractAction.extend({
        template: 'google_sheet_iframe', // Must match t-name in your XML

        start() {
            return this._super(...arguments);
        },
    });

    core.action_registry.add('google_sheet_dashboard', GoogleSheetDashboard);
    return GoogleSheetDashboard;
});
