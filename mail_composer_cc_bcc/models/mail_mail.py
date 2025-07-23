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
        res = super()._prepare_outgoing_list(recipients_follower_status=recipients_follower_status)

        if len(self.ids) > 1 or not self.env.context.get("is_from_composer"):
            return res

        mail = self[0]

        # Separate partners
        partners_cc_bcc = mail.recipient_cc_ids + mail.recipient_bcc_ids
        partner_to_ids = [p.id for p in mail.recipient_ids if p not in partners_cc_bcc]
        partner_to = self.env["res.partner"].browse(partner_to_ids)

        # Format headers
        email_to = format_emails(partner_to)
        email_to_raw = format_emails_raw(partner_to)
        email_cc = format_emails(mail.recipient_cc_ids)

        base_msg = res[0] if res else {}
        base_msg.update({
            "email_to": email_to,
            "email_to_raw": email_to_raw,
            "email_cc": email_cc,
            "email_bcc": "",  # Clear global Bcc
        })

        result = [base_msg]

        # Generate separate emails for each BCC partner
        for partner in mail.recipient_bcc_ids:
            if not partner.email:
                continue

            bcc_email = tools.email_normalize(partner.email)
            bcc_msg = dict(base_msg)  # Clean shallow copy

            # Deep copy headers to avoid overwriting base_msg
            bcc_msg["headers"] = dict(bcc_msg.get("headers", {}))
            bcc_msg["headers"]["X-Odoo-Bcc"] = bcc_email

            # Insert BCC notice into body
            bcc_note = (
                "<p style='color:gray; font-size:small;'>"
                "🔒 You received this email as a BCC (Blind Carbon Copy). "
                "Please do not reply to all.</p>"
            )
            bcc_msg["body"] = bcc_note + bcc_msg.get("body", "")

            # Override recipients
            bcc_msg["email_to"] = partner.email
            bcc_msg["email_cc"] = email_cc  # Keep same headers
            bcc_msg["email_bcc"] = ""
            bcc_msg["recipient_ids"] = [(6, 0, [partner.id])]

            result.append(bcc_msg)

        return result
