from odoo import models, fields

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    bcc_partner_ids = fields.Many2one('res.partner')

    def custom_send_email_with_bcc(self, body, subject, to_partner_id):
        if not to_partner_id:
            return
        bcc_emails = [partner.email for partner in self.bcc_partner_ids if partner.email]
        self.message_post(
            body=body,
            subject=subject,
            partner_ids=[to_partner_id.id],
            email_bcc=bcc_emails,
            message_type='email',
            subtype_xmlid='mail.mt_comment',
        )
