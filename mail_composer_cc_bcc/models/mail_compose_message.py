from odoo import models, fields


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    bcc_recipient_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Bcc",
        help="Partners who will receive a blind carbon copy of the email."
    )

    def _action_send_mail(self, auto_commit=False):
        res = super()._action_send_mail(auto_commit=auto_commit)

        mail_mail = self.env["mail.mail"]
        for wizard in self:
            if wizard.bcc_recipient_ids:
                mails = mail_mail.search([
                    ("mail_message_id", "=", wizard.mail_message_id.id)
                ])
                for mail in mails:
                    mail.recipient_bcc_ids = [(6, 0, wizard.bcc_recipient_ids.ids)]

        return res
