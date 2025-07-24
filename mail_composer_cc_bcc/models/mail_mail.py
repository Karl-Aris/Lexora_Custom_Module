# Inherit from mail.mail
from odoo import models
from odoo.tools import email_split
import json


class MailMail(models.Model):
    _inherit = "mail.mail"

    def _split_recipient_list(self):
        result = self.browse()
        for mail in self:
            bcc_list = email_split(mail.bcc)
            if not bcc_list:
                result |= mail
                continue

            # Original email: To + Cc only, no Bcc
            result |= mail.copy(default={
                'bcc': False,
                'headers': self._patch_headers_with_x_odoo_bcc(mail.headers, None),
            })

            # Create separate mail for each Bcc recipient
            for bcc_recipient in bcc_list:
                result |= mail.copy(default={
                    'email_to': mail.email_to,
                    'email_cc': mail.email_cc,
                    'bcc': False,
                    'headers': self._patch_headers_with_x_odoo_bcc(mail.headers, bcc_recipient),
                })
        return result

    def _patch_headers_with_x_odoo_bcc(self, headers, bcc_value):
        try:
            headers_dict = json.loads(headers or '{}')
        except Exception:
            headers_dict = {}

        if bcc_value:
            headers_dict["X-Odoo-Bcc"] = bcc_value
        else:
            headers_dict.pop("X-Odoo-Bcc", None)

        return json.dumps(headers_dict)
