# helpdesk_bcc_extension/models/mail_message.py
from odoo import models, fields

class MailMessage(models.Model):
    _inherit = 'mail.message'

    recipient_cc_ids = fields.Many2many('res.partner', string='CC Recipients')


    def _notify(self, force_send=False, send_after_commit=True, user_signature=True):
        notifications = super()._notify(
            force_send=force_send,
            send_after_commit=send_after_commit,
            user_signature=user_signature,
        )

        for msg in self:
            if msg.model == 'helpdesk.ticket' and msg.res_id:
                ticket = self.env['helpdesk.ticket'].browse(msg.res_id)
                bcc_partners = ticket.bcc_partner_ids
                bcc_notif = msg._notify_record_by_email(bcc_partners, force_send=force_send, send_after_commit=send_after_commit)
                notifications |= bcc_notif
        return notifications
