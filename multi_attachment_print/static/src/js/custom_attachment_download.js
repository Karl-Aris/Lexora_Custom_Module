/** @odoo-module **/

import { registry } from "@web/core/registry";
import { ClientAction } from "@web/core/client_action/client_action";

class MultiAttachmentDownload extends ClientAction {
    setup() {
        const attachment_ids = this.props.action.context.attachment_ids || [];

        for (const id of attachment_ids) {
            const url = `/web/content/${id}?download=true`;
            window.open(url, '_blank');
        }

        // Close the action after a short delay
        setTimeout(() => {
            this.props.closeAction();
        }, 500);
    }
}

registry.category("client_actions").add("multi_attachment_download", MultiAttachmentDownload);
