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

        if len(self.ids) > 1 or not self.env.context.get("is_from_composer", False):
            return res

        # Prepare email headers
        partners_cc_bcc = self.recipient_cc_ids + self.recipient_bcc_ids
        partner_to = self.recipient_ids - partners_cc_bcc
        email_to = format_emails(partner_to)
        email_to_raw = format_emails_raw(partner_to)
        email_cc = format_emails(self.recipient_cc_ids)
        email_bcc_list = [r.email for r in self.recipient_bcc_ids if r.email]

        recipients = set()

        for m in res:
            rcpt_to = None

            # Detect actual envelope recipient (for header-only personalization)
            if m.get("email_to"):
                rcpt_to = extract_rfc2822_addresses(m["email_to"][0])[0]
            elif m.get("email_cc"):
                rcpt_to = extract_rfc2822_addresses(m["email_cc"][0])[0]

            if rcpt_to:
                recipients.add(rcpt_to)

                if rcpt_to in email_bcc_list:
                    # Tag with X-Odoo-Bcc header
                    m["headers"].update({"X-Odoo-Bcc": m["email_to"][0]})

                    # Add visible BCC warning note to body
                    bcc_note = (
                        "<p style='color:gray; font-style:italic;'>"
                        "🔒 You received this email as a BCC (Blind Carbon Copy). "
                        "Please do not reply to all.</p>"
                    )
                    body = m.get("body", "") or ""
                    m["body"] = bcc_note + body
                    m["body_html"] = m["body"]

            # Update headers for all messages
            m.update({
                "email_to": email_to,
                "email_to_raw": email_to_raw,
                "email_cc": email_cc,
                "email_bcc": "",  # hide actual BCC in outgoing msg
            })

        self.env.context = {**self.env.context, "recipients": list(recipients)}

        # Prevent duplicate message generation
        if len(res) > len(recipients):
            res = res[:len(recipients)]

        return res
