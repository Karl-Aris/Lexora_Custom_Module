/** @odoo-module **/

import { registry } from "@web/core/registry";
import { AbstractAction } from "@web/core/action/action_service";

class MultiAttachmentDownload extends AbstractAction {
    async setup() {
        const attachment_ids = this.props.action.context.attachment_ids || [];

        for (const id of attachment_ids) {
            const url = `/web/content/${id}?download=true`;
            window.open(url, '_blank');
        }

        // Close the action
        this.props.closeAction();
    }
}

registry.category("actions").add("multi_attachment_download", MultiAttachmentDownload);
