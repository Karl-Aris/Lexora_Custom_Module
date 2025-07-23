from odoo import models, _
from odoo.exceptions import UserError
import copy


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def _prepare_outgoing_list(self):
        self.ensure_one()

        mail_values_dict = self._get_mail_values([self.id])
        mail_values = mail_values_dict.get(self.id)
        if not mail_values:
            raise UserError(_("Could not generate mail values for this message."))

        mail_values_list = []

        standard_mail_values = copy.deepcopy(mail_values)
        standard_mail_values["email_to"] = ','.join(
            p.email for p in self.recipient_ids if p.email
        )
        standard_mail_values["email_cc"] = ','.join(
            p.email for p in getattr(self, 'recipient_cc_ids', []) if p.email
        )
        standard_mail_values["email_bcc"] = ','.join(
            p.email for p in getattr(self, 'recipient_bcc_ids', []) if p.email
        )

        mail_values_list.append(standard_mail_values)

        return mail_values_list
