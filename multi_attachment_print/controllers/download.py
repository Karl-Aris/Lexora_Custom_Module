from odoo import http
from odoo.http import request
import json

class MultiAttachmentDownloadController(http.Controller):

    @http.route('/multi_attachment/download_urls', type='json', auth='user')
    def get_download_urls(self):
        # Adjust this to suit your model and filtering logic
        record_ids = request.params.get('record_ids', [])
        model = request.params.get('model')

        if not model or not record_ids:
            return []

        records = request.env[model].browse(record_ids)

        urls = []
        for rec in records:
            for attachment in rec.attachment_ids:
                urls.append(f'/web/content/{attachment.id}?download=true')

        return urls
