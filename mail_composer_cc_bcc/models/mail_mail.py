# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, tools
from odoo.addons.base.models.ir_mail_server import extract_rfc2822_addresses


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

        # Prepare values for To, Cc headers
        partners_cc_bcc = self.recipient_cc_ids + self.recipient_bcc_ids
        partner_to_ids = [r.id for r in self.recipient_ids if r not in partners_cc_bcc]
        partner_to = self.env["res.partner"].browse(partner_to_ids)
        email_to = format_emails(partner_to)
        email_to_raw = format_emails_raw(partner_to)
        email_cc = format_emails(self.recipient_cc_ids)
        email_bcc = [tools.email_normalize(r.email) for r in self.recipient_bcc_ids if r.email]

        recipients = set()

        for m in res:
            rcpt_to = None
            recipient_email = ""

            if m["email_to"]:
                recipient_email = extract_rfc2822_addresses(m["email_to"][0])[0]
                rcpt_to = recipient_email
            elif m.get("email_cc"):
                recipient_email = extract_rfc2822_addresses(m["email_cc"][0])[0]
                rcpt_to = recipient_email

            if rcpt_to:
                recipients.add(rcpt_to)

                if tools.email_normalize(rcpt_to) in email_bcc:
                    # Inject BCC note in body
                    bcc_note = (
                        "<p style='color:gray; font-style:italic;'>"
                        "🔒 You received this email as a BCC (Blind Carbon Copy). "
                        "Please do not reply to all.</p>"
                    )
                    m["body"] = bcc_note + m.get("body", "")
                    m["body_html"] = m["body"]
                    m["headers"].update({"X-Odoo-Bcc": m["email_to"][0]})

            m.update(
                {
                    "email_to": email_to,
                    "email_to_raw": email_to_raw,
                    "email_cc": email_cc,
                }
            )

        self.env.context = {**self.env.context, "recipients": list(recipients)}

        if len(res) > len(recipients):
            res.pop()

        return res
