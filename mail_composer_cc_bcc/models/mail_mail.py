from odoo import fields, models, tools


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
        base_res = super()._prepare_outgoing_list(recipients_follower_status=recipients_follower_status)

        if len(self.ids) != 1 or not self.env.context.get("is_from_composer", False):
            return base_res

        mail = self[0]

        # Separate partner groups
        bcc_partners = mail.recipient_bcc_ids
        cc_partners = mail.recipient_cc_ids
        to_partners = mail.recipient_ids - cc_partners - bcc_partners

        # Email headers
        email_to = format_emails(to_partners)
        email_to_raw = format_emails_raw(to_partners)
        email_cc = format_emails(cc_partners)

        base_msg = base_res[0] if base_res else {}
        original_body = base_msg.get("body", "")
        original_headers = base_msg.get("headers", {}).copy()

        result = []

        # ➤ Message for To + Cc (no BCC note)
        if to_partners or cc_partners:
            result.append({
                "subject": base_msg.get("subject", ""),
                "body": original_body,
                "email_to": email_to,
                "email_to_raw": email_to_raw,
                "email_cc": email_cc,
                "email_bcc": "",  # never expose bcc
                "headers": original_headers.copy(),
                "recipient_ids": [(6, 0, (to_partners + cc_partners).ids)],
                "attachments": base_msg.get("attachments", []),
                "message_id": base_msg.get("message_id", False),
            })

        # ➤ Separate email for each BCC with BCC note
        for bcc_partner in bcc_partners:
            if not bcc_partner.email:
                continue

            bcc_email = tools.email_normalize(bcc_partner.email)
            bcc_note = (
                "<p style='color:gray; font-size:small;'>"
                "🔒 You received this email as a BCC (Blind Carbon Copy). "
                "Please do not reply to all.</p>"
            )

            result.append({
                "subject": base_msg.get("subject", ""),
                "body": bcc_note + original_body,
                "email_to": bcc_email,
                "email_to_raw": bcc_email,
                "email_cc": email_cc,
                "email_bcc": "",  # still no real bcc
                "headers": {
                    **original_headers,
                    "X-Odoo-Bcc": bcc_email,
                },
                "recipient_ids": [(6, 0, [bcc_partner.id])],
                "attachments": base_msg.get("attachments", []),
                "message_id": base_msg.get("message_id", False),
            })

        return result
