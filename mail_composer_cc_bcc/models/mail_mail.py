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

        # Limit scope only to single-message calls (not bulk)
        if len(self.ids) > 1 or not self.env.context.get("is_from_composer", False):
            return res

        # Prepare values for To, Cc headers
        all_cc_bcc = self.recipient_cc_ids + self.recipient_bcc_ids
        to_partners = [r for r in self.recipient_ids if r not in all_cc_bcc]

        email_to = format_emails(to_partners)
        email_to_raw = format_emails_raw(to_partners)
        email_cc = format_emails(self.recipient_cc_ids)
        email_bcc_list = [r.email for r in self.recipient_bcc_ids if r.email]

        recipients = set()
        for m in res:
            rcpt_to = None
            if m.get("email_to"):
                rcpt_to = extract_rfc2822_addresses(m["email_to"][0])[0]
            elif m.get("email_cc"):
                rcpt_to = extract_rfc2822_addresses(m["email_cc"][0])[0]

            if rcpt_to:
                recipients.add(rcpt_to)

            # Identify BCC message and add note
            if rcpt_to in email_bcc_list:
                m["headers"].update({"X-Odoo-Bcc": m["email_to"][0]})
                bcc_html_note = (
                    "<br/><br/><hr/><p><strong>🔒 You received this email as a BCC "
                    "(Blind Carbon Copy). Please do not reply to all.</strong></p>"
                )
                bcc_text_note = (
                    "\n\n---\n🔒 You received this email as a BCC "
                    "(Blind Carbon Copy). Please do not reply to all."
                )
                if "body_html" in m and m["body_html"]:
                    m["body_html"] += bcc_html_note
                elif "body" in m and m["body"]:
                    m["body"] += bcc_text_note

            # Set standard headers (all recipients see same To/CC headers)
            m.update({
                "email_to": email_to,
                "email_to_raw": email_to_raw,
                "email_cc": email_cc,
            })

        self.env.context = {**self.env.context, "recipients": list(recipients)}

        if len(res) > len(recipients):
            res = res[:len(recipients)]

        return res
