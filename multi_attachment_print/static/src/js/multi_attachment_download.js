/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class MultiAttachmentDownload extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        this.downloadAttachments();
    }

    async downloadAttachments() {
        try {
            const urls = await this.rpc("/multi_attachment/download_urls", {
                model: this.props.model,
                record_ids: this.props.resIds,
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
            this.notification.add("Download failed", { type: "danger" });
            console.error("Download error", error);
        }
    }

    // no template needed
    static template = null;
}

registry.category("action").add("multi_attachment_download", MultiAttachmentDownload);
