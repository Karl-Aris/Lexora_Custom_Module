from odoo import fields, models, tools
from odoo.addons.base.models.ir_mail_server import extract_rfc2822_addresses

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
        is_out_of_scope = len(self.ids) > 1
        is_from_composer = self.env.context.get("is_from_composer", False)

        if is_out_of_scope or not is_from_composer:
            return res

        mail = self[0]

        partners_cc_bcc = mail.recipient_cc_ids + mail.recipient_bcc_ids
        partner_to_ids = [r.id for r in mail.recipient_ids if r not in partners_cc_bcc]
        partner_to = self.env["res.partner"].browse(partner_to_ids)

        email_to = format_emails(partner_to)
        email_to_raw = format_emails_raw(partner_to)
        email_cc = format_emails(mail.recipient_cc_ids)

        base_msg = res[0] if res else {}
        original_body = res[0].get("body", "") if res else ""

        # To & CC message (no BCC note)
        clean_msg = base_msg.copy()
        clean_msg.update({
            "email_to": email_to,
            "email_to_raw": email_to_raw,
            "email_cc": email_cc,
            "email_bcc": "",
            "body": original_body,
            "recipient_ids": [(6, 0, [p.id for p in partner_to + mail.recipient_cc_ids])],
        })

        result = [clean_msg]

        # Add one message per BCC recipient
        for partner in mail.recipient_bcc_ids:
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
                "headers": {
                    **base_msg.get("headers", {}),
                    "X-Odoo-Bcc": bcc_email
                },
                "email_to": email_to_raw,   # show original To
                "email_cc": email_cc,       # show original CC
                "email_bcc": "",            # hide actual Bcc
                "body": bcc_note + original_body,  # add BCC note
                "recipient_ids": [(6, 0, [partner.id])],  # send only to this BCC partner
            })

            result.append(bcc_msg)

        return result
