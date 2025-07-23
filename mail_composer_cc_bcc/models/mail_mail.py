from odoo import fields, models, tools

def format_emails(partners):
    emails = [
        tools.formataddr((p.name or "", tools.email_normalize(p.email)))
        for p in partners if p.email
    ]
    return ", ".join(emails)

def format_emails_raw(partners):
    emails = [p.email for p in partners if p.email]
    return ", ".join(emails)

class MailMail(models.Model):
    _inherit = "mail.mail"

    email_bcc = fields.Char("Bcc", help="Blind Cc message recipients")

    def _prepare_outgoing_list(self, recipients_follower_status=None):
        res = super()._prepare_outgoing_list(recipients_follower_status=recipients_follower_status)
        if not res or len(self.ids) != 1 or not self.env.context.get("is_from_composer", False):
            return res

        mail = self[0]

        # Identify recipient groups
        to_partners = mail.recipient_ids - mail.recipient_cc_ids - mail.recipient_bcc_ids
        cc_partners = mail.recipient_cc_ids
        bcc_partners = mail.recipient_bcc_ids

        # Format headers
        email_to = format_emails(to_partners)
        email_to_raw = format_emails_raw(to_partners)
        email_cc = format_emails(cc_partners)

        base_msg = res[0]
        original_body = base_msg.get("body", "")  # Keep this immutable

        result = []

        # 1. Clean version for TO + CC (no BCC note)
        clean_msg = base_msg.copy()
        clean_msg.update({
            "email_to": email_to,
            "email_to_raw": email_to_raw,
            "email_cc": email_cc,
            "email_bcc": "",
            "body": original_body,
            "recipient_ids": [(6, 0, (to_partners | cc_partners).ids)],
        })
        result.append(clean_msg)

        # 2. BCC version — one per partner
        for partner in bcc_partners:
            if not partner.email:
                continue

            bcc_email = tools.email_normalize(partner.email)
            bcc_note = (
                "<p style='color:gray; font-size:small;'>"
                "🔒 You received this email as a BCC (Blind Carbon Copy). "
                "Please do not reply to all.</p>"
            )

            bcc_msg = base_msg.copy()
            bcc_msg.update({
                "email_to": email_to_raw,
                "email_cc": email_cc,
                "email_bcc": "",  # Don't expose any BCC
                "headers": {
                    **base_msg.get("headers", {}),
                    "X-Odoo-Bcc": bcc_email
                },
                "body": bcc_note + original_body,
                "recipient_ids": [(6, 0, [partner.id])],
            })
            result.append(bcc_msg)

        return result
