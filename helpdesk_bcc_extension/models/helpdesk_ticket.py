from odoo import models, api

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    def custom_send_email_with_bcc(self, body, subject, to_partner_id, bcc_emails):
        if not to_partner_id:
            return
        self.message_post(
            body=body,
            subject=subject,
            partner_ids=[to_partner_id.id],
            email_bcc=bcc_emails,
            message_type='email',
            subtype_xmlid='mail.mt_comment',
            reply_to='support@yourdomain.com'
        )
