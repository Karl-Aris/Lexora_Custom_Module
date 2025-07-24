# mail_mail.py
# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, tools
from odoo.addons.base.models.ir_mail_server import extract_rfc2822_addresses
from email.utils import parseaddr

def format_emails(partners):
    emails = [
        tools.formataddr((p.name or "", tools.email_normalize(p.email)))
        for p in partners
        if p.email
    ]
    return ", ".join(emails)

def format_emails_raw(partners):
    emails = [p.email for p in partners if p.email]
    return ", ".join(emails)

class MailMail(models.Model):
    _inherit = "mail.mail"

    email_bcc = fields.Char("Bcc", help="Blind Cc message recipients")

    def _prepare_outgoing_list(self, recipients_follower_status=None):
        res = super()._prepare_outgoing_list(
            recipients_follower_status=recipients_follower_status
        )
        is_out_of_scope = len(self.ids) > 1
        is_from_composer = self.env.context.get("is_from_composer", False)

        if is_out_of_scope or not is_from_composer:
            return res

        partners_cc_bcc = self.recipient_cc_ids + self.recipient_bcc_ids
        partner_to_ids = [r.id for r in self.recipient_ids if r not in partners_cc_bcc]
        partner_to = self.env["res.partner"].browse(partner_to_ids)
        email_to = format_emails(partner_to)
        email_to_raw = format_emails_raw(partner_to)
        email_cc = format_emails(self.recipient_cc_ids)
        email_bcc = [r.email for r in self.recipient_bcc_ids if r.email]

        recipients = set()
        filtered_res = []

        for m in res:
            rcpt_to_email = None
            rcpt_to_full = m.get("email_to") and m["email_to"][0]
            if rcpt_to_full:
                rcpt_to_email = parseaddr(rcpt_to_full)[1]

            if rcpt_to_email in email_bcc:
                m["headers"].update({"X-Odoo-Bcc": rcpt_to_full})
                m.update({
                    "email_to": rcpt_to_full,
                    "email_to_raw": rcpt_to_email,
                    "email_cc": "",
                })
            else:
                m.update({
                    "email_to": email_to,
                    "email_to_raw": email_to_raw,
                    "email_cc": email_cc,
                })

            filtered_res.append(m)
            recipients.add(rcpt_to_email or "general")

        self.env.context = {**self.env.context, "recipients": list(recipients)}
        return filtered_res
