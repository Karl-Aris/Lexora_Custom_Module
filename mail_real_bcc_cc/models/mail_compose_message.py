from odoo import models, fields

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    cc_partner_ids = fields.Many2many(
        'res.partner',
        relation='mail_compose_cc_partner_rel',
        string='CC'
    )
    bcc_partner_ids = fields.Many2many(
        'res.partner',
        relation='mail_compose_bcc_partner_rel',
        string='BCC'
    )

    def action_send_mail(self):
        res = super().action_send_mail()
        if not self.env.context.get('mail_mail_created_ids'):
            return res

        mails = self.env['mail.mail'].browse(self.env.context.get('mail_mail_created_ids'))
        for mail in mails:
            if self.cc_partner_ids:
                mail.email_cc = ','.join(self.cc_partner_ids.mapped('email'))
            if self.bcc_partner_ids:
                bcc_emails = self.bcc_partner_ids.mapped('email')
                mail.email_bcc = ','.join(bcc_emails)
                if mail.email_to:
                    mail.email_to = ','.join(
                        e for e in mail.email_to.split(',') if e.strip() not in bcc_emails
                    )
        return res
