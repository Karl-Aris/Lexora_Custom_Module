from odoo import models, fields, api
import base64
import zipfile
import io

class AttachmentSelectionLine(models.Model):
    _name = 'attachment.selection.line'
    _description = "Attachment Selection Line"

    sale_order_id = fields.Many2one('sale.order', string="Sale Order", required=True, ondelete='cascade')
    attachment_id = fields.Many2one('ir.attachment', string="Attachment", required=True)
    name = fields.Char(related='attachment_id.name', string="Name", store=True)
    selected = fields.Boolean(default=True)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    attachment_selection_line_ids = fields.One2many(
        'attachment.selection.line', 'sale_order_id', string="Attachment Selections")

    def action_download_selected_attachments(self):
        selected_attachments = self.attachment_selection_line_ids.filtered(lambda l: l.selected)
        if not selected_attachments:
            return

        zip_buffer = io.BytesIO()
        name_counter = {}
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for line in selected_attachments:
                if line.attachment_id.datas:
                    name = line.attachment_id.name or 'unnamed'
                    count = name_counter.get(name, 0) + 1
                    name_counter[name] = count
                    filename = name if count == 1 else f"{name.rsplit('.', 1)[0]}_{count}.{name.rsplit('.', 1)[-1]}"
                    zip_file.writestr(filename, base64.b64decode(line.attachment_id.datas))
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

    def sync_attachment_selection_lines(self):
        for order in self:
            existing_attachment_ids = order.attachment_selection_line_ids.mapped('attachment_id').ids
            attachments = self.env['ir.attachment'].search([
                ('res_model', '=', 'sale.order'),
                ('res_id', '=', order.id),
                ('type', '=', 'binary')
            ])
            for att in attachments:
                if att.id not in existing_attachment_ids:
                    self.env['attachment.selection.line'].create({
                        'sale_order_id': order.id,
                        'attachment_id': att.id,
                        'selected': True,
                    })
