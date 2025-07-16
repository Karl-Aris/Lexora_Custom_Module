/** @odoo-module **/

import { registry } from "@web/core/registry";
import { AbstractAction } from "@web/webclient/actions/abstract_action";
import { useService } from "@web/core/utils/hooks";

class MultiAttachmentDownload extends AbstractAction {
    setup() {
        super.setup();
        this.rpc = useService("rpc");
        this.notification = useService("notification");
    }

    async start() {
        try {
            // Example RPC to fetch attachment URLs
            const attachments = await this.rpc("/your/custom/download/url", {});

            for (const url of attachments) {
                const link = document.createElement("a");
                link.href = url;
                link.download = "";
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
        } catch (err) {
            this.notification.add("Failed to download attachments.", { type: "danger" });
            console.error("multi_attachment_download error:", err);
        }
    }
}

registry.action.add("multi_attachment_download", MultiAttachmentDownload);

export default MultiAttachmentDownload;
