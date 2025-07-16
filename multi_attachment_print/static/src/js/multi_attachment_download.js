/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("action").add("multi_attachment_download", {
    async execute(env, action) {
        try {
            const urls = await env.services.rpc("/multi_attachment/download_urls", {
                attachment_ids: action.context.attachment_ids,
            });

            for (const url of urls) {
                const a = document.createElement("a");
                a.href = url;
                a.download = "";
                a.style.display = "none";
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            }
        } catch (error) {
            env.services.notification.add("Download failed", { type: "danger" });
            console.error("Download error", error);
        }
    },
});
