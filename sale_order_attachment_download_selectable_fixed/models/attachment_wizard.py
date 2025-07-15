from odoo import models, fields, api

class AttachmentSelectionLine(models.Model):
    _name = 'attachment.selection.line'
    _description = "Attachment Selection Line"

    sale_order_id = fields.Many2one('sale.order', string="Sale Order", required=True, ondelete='cascade')
    attachment_id = fields.Many2one('ir.attachment', string="Attachment", required=True)
    name = fields.Char(related='attachment_id.name', string="Name", store=True)
    selected = fields.Boolean(default=True)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    attachment_selection_line_ids = fields.One2many('attachment.selection.line', 'sale_order_id', string="Attachment Selections")

    def action_download_selected_attachments(self):
        import base64
        import zipfile
        import io

        selected_attachments = self.attachment_selection_line_ids.filtered(lambda l: l.selected)
        if not selected_attachments:
            return
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for line in selected_attachments:
                if line.attachment_id.datas:
                    zip_file.writestr(
                        line.attachment_id.name,
                        base64.b64decode(line.attachment_id.datas)
                    )
        zip_buffer.seek(0)
        attachment = self.env['ir.attachment'].create({
            'name': 'selected_attachments.zip',
            'type': 'binary',
            'datas': base64.b64encode(zip_buffer.read()),
            'res_model': 'sale.order',
            'res_id': self.id,
        })
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    @api.model
    def create_attachment_selection_lines(self):
        """ Helper method to sync sale order attachments to selection lines """
        for order in self:
            existing_lines = order.attachment_selection_line_ids.mapped('attachment_id').ids
            attachments = self.env['ir.attachment'].search([
                ('res_model', '=', 'sale.order'),
                ('res_id', '=', order.id)
            ])
            for att in attachments:
                if att.id not in existing_lines:
                    self.env['attachment.selection.line'].create({
                        'sale_order_id': order.id,
                        'attachment_id': att.id,
                        'selected': True,
                    })
