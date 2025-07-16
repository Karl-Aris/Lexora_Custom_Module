/** @odoo-module **/

import AbstractAction from 'web.AbstractAction';
import { registry } from '@web/core/registry/action';

export class MultiAttachmentDownload extends AbstractAction {
    async start() {
        const attachment_ids = this.props.action.context.attachment_ids || [];
        for (const id of attachment_ids) {
            const url = `/web/content/${id}?download=true`;
            window.open(url, '_blank');
        }
        this.env.services.action.doAction({ type: 'ir.actions.act_window_close' });
    }
}

registry.category('actions').add('multi_attachment_download', MultiAttachmentDownload);
