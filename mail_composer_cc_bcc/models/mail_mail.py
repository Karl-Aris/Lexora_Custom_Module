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
                if rcpt_to in email_bcc:
                    m["headers"].update({"X-Odoo-Bcc": m["email_to"][0]})

                    # Inject Bcc notice in HTML body if present
                    if "body_html" in m:
                        m["body_html"] += (
                            "<br><hr><small style=\"color:gray\">"
                            "Note: You are receiving this email as a Bcc recipient. "
                            "Please do not reply directly to this message."
                            "</small>"
                        )
                    if "body" in m:
                        m["body"] += (
                            "\n\nNote: You are receiving this email as a Bcc recipient. "
                            "Please do not reply directly to this message."
                        )

            elif m["email_cc"]:
                rcpt_to = extract_rfc2822_addresses(m["email_cc"][0])[0]

            if rcpt_to:
                recipients.add(rcpt_to)

            m.update({
                "email_to": email_to,
                "email_to_raw": email_to_raw,
                "email_cc": email_cc,
            })

        self.env.context = {**self.env.context, "recipients": list(recipients)}

        if len(res) > len(recipients):
            res.pop()

        return res
