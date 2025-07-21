from odoo import api, models

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.model
    def _action_send_mail(self, auto_commit=False):
        mails, messages = super()._action_send_mail(auto_commit=auto_commit)

        ctx = self.env.context
        bcc_partner_ids = ctx.get('default_partner_bcc_ids', [])
        bcc_emails = ctx.get('default_bcc_emails', False)

        emails = set()
        if isinstance(bcc_partner_ids, (list, tuple)) and bcc_partner_ids:
            partner_ids = bcc_partner_ids[2] if len(bcc_partner_ids) >= 3 else bcc_partner_ids
            for partner in self.env['res.partner'].browse(partner_ids):
                if partner.email:
                    emails.add(partner.email)
        if bcc_emails:
            emails.update([e.strip() for e in bcc_emails.split(',') if e.strip()])

        if emails:
            for mail in mails:
                mail.write({'email_bcc': ','.join(emails)})

        for mail in mails:
            mail.send(auto_commit=auto_commit)
        return mails, messages
