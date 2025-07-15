from odoo import models, fields, api

class AttachmentSelectionLine(models.TransientModel):
    _name = 'attachment.selection.line'

    wizard_id = fields.Many2one('sale.order.attachment.wizard', required=True, ondelete='cascade')
    attachment_id = fields.Many2one('ir.attachment', string="Attachment", required=True)
    name = fields.Char(related='attachment_id.name', string="Name", store=True)
    selected = fields.Boolean(default=True)

class SaleOrderAttachmentWizard(models.TransientModel):
    _name = 'sale.order.attachment.wizard'

    sale_order_id = fields.Many2one('sale.order', string="Sale Order", required=True)
    attachment_ids = fields.One2many('attachment.selection.line', 'wizard_id', string="Attachments")

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        sale_order_id = self.env.context.get('active_id')
        res['sale_order_id'] = sale_order_id
        sale_order = self.env['sale.order'].browse(sale_order_id)
        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'sale.order'),
            ('res_id', '=', sale_order.id)
        ])
        res['attachment_ids'] = [(0, 0, {
            'attachment_id': att.id,
            'selected': True
        }) for att in attachments]
        return res

    def action_download_selected(self):
        import base64
        import zipfile
        import io
        selected_attachments = self.attachment_ids.filtered(lambda l: l.selected)
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for line in selected_attachments:
                if line.attachment_id.datas:
                    zip_file.writestr(
                        line.attachment_id.name,
                        base64.b64decode(line.attachment_id.datas)
                    )
        zip_buffer.seek(0)
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content?model=sale.order.attachment.wizard&id=%d&field=dummy&download=true&filename=%s' % (
                self.id, 'selected_attachments.zip'),
            'target': 'self',
        }