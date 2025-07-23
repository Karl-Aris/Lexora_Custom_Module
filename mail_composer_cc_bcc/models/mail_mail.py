import re
from odoo import fields, models, tools
from odoo.addons.base.models.ir_mail_server import extract_rfc2822_addresses


def format_emails(partners):
    return ", ".join([
        tools.formataddr((p.name or "", tools.email_normalize(p.email)))
        for p in partners if p.email
    ])


def format_emails_raw(partners):
    return ", ".join([p.email for p in partners if p.email])


def html_to_text(html):
    """Robust HTML to plain text."""
    try:
        text = re.sub(r'<(br|p|div|li)[^>]*>', '\n', html, flags=re.I)
        text = re.sub(r'<[^>]+?>', '', text)  # Remove other tags
        text = re.sub(r'\s+', ' ', text)      # Collapse whitespace
        return text.strip()
    except Exception:
        return "This is a plain-text fallback of the email body."


class MailMail(models.Model):
    _inherit = "mail.mail"

    email_bcc = fields.Char("Bcc", help="Blind Cc message recipients")

    def _prepare_outgoing_list(self, recipients_follower_status=None):
        res = super()._prepare_outgoing_list(recipients_follower_status=recipients_follower_status)

        if len(self.ids) > 1 or not self.env.context.get("is_from_composer", False):
            return res

        mail = self[0]

        bcc_partners = mail.recipient_bcc_ids
        cc_partners = mail.recipient_cc_ids
        all_cc_bcc = cc_partners + bcc_partners

        to_partners = self.env["res.partner"].browse([
            p.id for p in mail.recipient_ids if p not in all_cc_bcc
        ])

        email_to = format_emails(to_partners)
        email_to_raw = format_emails_raw(to_partners)
        email_cc = format_emails(cc_partners)

        base_msg = res[0] if res else {}
        original_body = base_msg.get("body", "") or ""
        original_alt = html_to_text(original_body) or "You received an email."

        clean_msg = base_msg.copy()
        clean_msg.update({
            "email_to": email_to,
            "email_to_raw": email_to_raw,
            "email_cc": email_cc,
            "email_bcc": "",
            "body": original_body,
            "body_alternative": original_alt,
            "recipient_ids": [(6, 0, [p.id for p in to_partners + cc_partners])],
        })

        result = [clean_msg]

        # Build BCC variants
        for partner in bcc_partners:
            if not partner.email:
                continue

            bcc_email = tools.email_normalize(partner.email)

            bcc_note = (
                "<p style='color:gray; font-size:small;'>"
                "🔒 You received this email as a BCC (Blind Carbon Copy). "
                "Please do not reply to all.</p>"
            )
            bcc_body = bcc_note + original_body
            bcc_alt = html_to_text(bcc_body) or "You received this email as a BCC."

            bcc_msg = base_msg.copy()
            bcc_msg.update({
                "headers": {**base_msg.get("headers", {}), "X-Odoo-Bcc": bcc_email},
                "email_to": partner.email,
                "email_to_raw": partner.email,
                "email_cc": email_cc,
                "email_bcc": "",
                "body": bcc_body,
                "body_alternative": bcc_alt,
                "recipient_ids": [(6, 0, [partner.id])],
            })

            result.append(bcc_msg)

        return result
