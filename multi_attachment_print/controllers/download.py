from odoo import http
from odoo.http import request
import base64
import io
import zipfile


class MultiAttachmentDownloadController(http.Controller):

    @http.route('/download/attachments_by_ids', type='http', auth="user")
    def download_attachments_by_ids(self, ids=None):
        if not ids:
            return request.not_found()

        attachment_ids = [int(i) for i in ids.split(',') if i]
        attachments = request.env['ir.attachment'].sudo().browse(attachment_ids)

        zip_stream = io.BytesIO()
        with zipfile.ZipFile(zip_stream, 'w') as zip_file:
            for att in attachments:
                if att.type == 'binary' and att.datas:
                    zip_file.writestr(att.name or f'file_{att.id}', base64.b64decode(att.datas))

        zip_stream.seek(0)
        return request.make_response(
            zip_stream.read(),
            headers=[
                ('Content-Type', 'application/zip'),
                ('Content-Disposition', 'attachment; filename="attachments.zip"')
            ]
        )
