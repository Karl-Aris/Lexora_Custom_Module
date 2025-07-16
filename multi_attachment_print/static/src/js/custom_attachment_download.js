/** @odoo-module **/

import { registry } from "@web/core/registry";
import { download } from "@web/core/network/download";

registry.category("client_actions").add("multi_attachment_download", {
    async execute(env, action) {
        const ids = action.context.attachment_ids;
        if (!ids || !ids.length) {
            console.warn("No attachments to download.");
            return;
        }

        const url = `/download/attachments_by_ids?ids=${ids.join(",")}`;
        download({ url });
    },
});
