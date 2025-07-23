from odoo import models, fields


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    bcc_recipient_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="mail_compose_message_res_partner_bcc_rel",
        column1="mail_compose_message_id",  # This is the correct one
        column2="partner_id",
        string="Bcc",
        help="Partners who will receive a blind carbon copy of the email."
    )

    def _action_send_mail(self, auto_commit=False):
        res = super()._action_send_mail(auto_commit=auto_commit)

        Mail = self.env["mail.mail"]
        for wizard in self:
            if wizard.bcc_recipient_ids:
                mails = Mail.search([
                    ("mail_message_id", "=", wizard.mail_message_id.id)
                ])
                for mail in mails:
                    mail.recipient_bcc_ids = [(6, 0, wizard.bcc_recipient_ids.ids)]

        return res
