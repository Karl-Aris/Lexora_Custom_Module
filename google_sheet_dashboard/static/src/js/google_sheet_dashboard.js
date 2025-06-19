odoo.define('google_sheet_dashboard.google_sheet_dashboard', [
    'web.AbstractAction',
    'web.core'
], function (require) {
    'use strict';

    const AbstractAction = require('web.AbstractAction');
    const core = require('web.core');

    const GoogleSheetDashboard = AbstractAction.extend({
        template: 'google_sheet_iframe',

        start() {
            return this._super(...arguments);
        },
    });

    core.action_registry.add('google_sheet_dashboard', GoogleSheetDashboard);
    return GoogleSheetDashboard;
});
