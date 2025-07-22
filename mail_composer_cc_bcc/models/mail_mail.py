# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, tools
from odoo.addons.base.models.ir_mail_server import extract_rfc2822_addresses


def format_emails(partners):
    return ", ".join([
        tools.formataddr((p.name or "", tools.email_normalize(p.email)))
        for p in partners if p.email
    ])


def format_emails_raw(partners):
    return ", ".join([p.email for p in partners if p.email])


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
        for m in res:
            rcpt_to = None
            if m["email_to"]:
                rcpt_to = extract_rfc2822_addresses(m["email_to"][0])[0]
            elif m.get("email_cc"):
                rcpt_to = extract_rfc2822_addresses(m["email_cc"][0])[0]

            if rcpt_to:
                recipients.add(rcpt_to)

                if rcpt_to in email_bcc:
                    # Add technical header
                    m["headers"].update({"X-Odoo-Bcc": m["email_to"][0]})

                    # Inject visible notice
                    bcc_notice_html = "<p style='color:gray; font-style:italic;'>🔒 You received this email as a BCC (Blind Carbon Copy). Please do not reply.</p>"
                    bcc_notice_text = "🔒 You received this email as a BCC (Blind Carbon Copy). Please do not reply.\n\n"

                    if m.get("body_html"):
                        m["body_html"] = bcc_notice_html + m["body_html"]
                    if m.get("body"):
                        m["body"] = bcc_notice_text + m["body"]

            # Standardize visible To and CC headers
            m.update({
                "email_to": email_to,
                "email_to_raw": email_to_raw,
                "email_cc": email_cc,
            })

        self.env.context = {**self.env.context, "recipients": list(recipients)}

        if len(res) > len(recipients):
            res.pop()

        return res
