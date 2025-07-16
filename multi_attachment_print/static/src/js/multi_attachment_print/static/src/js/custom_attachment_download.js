odoo.define('multi_attachment_print.multi_attachment_download', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');

    var MultiAttachmentDownload = AbstractAction.extend({
        start: function () {
            var attachment_ids = this.action.context.attachment_ids || [];

            attachment_ids.forEach(function (id) {
                var url = `/web/content/${id}?download=true`;
                window.open(url, '_blank');
            });

            this.do_action('ir.actions.act_window_close');
            return Promise.resolve();
        },
    });

    core.action_registry.add('multi_attachment_download', MultiAttachmentDownload);
    return MultiAttachmentDownload;
});
