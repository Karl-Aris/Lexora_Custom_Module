from odoo import models, _
from odoo.exceptions import UserError
from odoo.tools import html2plaintext
import copy
import logging

_logger = logging.getLogger(__name__)

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def _prepare_outgoing_list(self):
        self.ensure_one()
        mail_values_dict = self._get_mail_values([self.id])
        mail_values = mail_values_dict.get(self.id)
        if not mail_values:
            raise UserError(_("Could not generate mail values."))
    
        mail_values_list = []
    
        # Standard TO + CC mail
        standard_to = ','.join(p.email for p in self.recipient_ids if p.email)
        standard_cc = ','.join(p.email for p in getattr(self, 'recipient_cc_ids', []))
        mail_values.update({
            'email_to': standard_to,
            'email_cc': standard_cc,
            'email_bcc': '',  # hide bcc
        })
        mail_values_list.append(mail_values)
    
        # BCC recipients get separate mail
        for partner in getattr(self, 'recipient_bcc_ids', []):
            if not partner.email:
                continue
            bcc_mail = copy.deepcopy(mail_values)
            bcc_mail.update({
                'email_to': partner.email,
                'email_cc': standard_cc,
                'email_bcc': '',
                'body': (
                    f"""
                    <p style="color:gray; font-size:small;">
                      <strong>From:</strong> {self.email_from or 'Lexora'}<br/>
                      <strong>Reply-To:</strong> {self.reply_to or self.email_from or 'Lexora'}<br/>
                      <strong>To:</strong> {standard_to}<br/>
                      <strong>Cc:</strong> {standard_cc}<br/>
                      <strong>Bcc:</strong> {partner.email}<br/>
                      <em>🔒 You received this email as a BCC. Do not reply all.</em>
                    </p>
                    """ + (bcc_mail.get("body", "") or "")
                ),
            })
            mail_values_list.append(bcc_mail)
    
        # Actually create mail.mail records!
        Mail = self.env['mail.mail'].sudo()
        mail_ids = []
        for values in mail_values_list:
            mail_id = Mail.create(values)
            mail_ids.append(mail_id.id)
    
        return self.env['mail.mail'].browse(mail_ids)
