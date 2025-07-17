from odoo import models, fields

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    bcc_partner_ids = fields.Many2many(
        'res.partner',
        'helpdesk_ticket_bcc_partner_rel',  # relation table name
        'ticket_id',                        # column for helpdesk.ticket ID
        'partner_id',                       # column for res.partner ID
        string='BCC Partners'
    )

    def custom_send_email_with_bcc(self, body, subject, to_partner_id):
        if not to_partner_id:
            return
        bcc_email = self.bcc_partner_id.email if self.bcc_partner_id and self.bcc_partner_id.email else False
        self.message_post(
            body=body,
            subject=subject,
            partner_ids=[to_partner_id.id],
            email_bcc=[bcc_email] if bcc_email else [],
            message_type='email',
            subtype_xmlid='mail.mt_comment',
        )
