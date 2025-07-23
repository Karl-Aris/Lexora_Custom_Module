from odoo import models, fields, tools
from odoo.addons.base.models.ir_mail_server import extract_rfc2822_addresses


def format_emails(partners):
    return ", ".join([
        tools.formataddr((p.name or "", tools.email_normalize(p.email)))
        for p in partners if p.email
    ])


class MailMail(models.Model):
    _inherit = "mail.mail"

    email_bcc = fields.Char("Bcc", help="Blind Cc message recipients")

    def _prepare_outgoing_list(self, recipients_follower_status=None):
        res = super()._prepare_outgoing_list(recipients_follower_status=recipients_follower_status)

        if len(self.ids) != 1 or not self.env.context.get("is_from_composer"):
            return res

        mail = self[0]
        recipient_to = mail.recipient_ids - mail.recipient_cc_ids - mail.recipient_bcc_ids
        recipient_cc = mail.recipient_cc_ids
        recipient_bcc = mail.recipient_bcc_ids

        email_to_header = format_emails(recipient_to)
        email_cc_header = format_emails(recipient_cc)
        bcc_emails = [tools.email_normalize(p.email) for p in recipient_bcc if p.email]

        final_msgs = []
        added = set()

        # Step 1: Send To + Cc message
        for msg in res:
            msg.update({
                "email_to": email_to_header,
                "email_cc": email_cc_header,
                "email_bcc": False,
            })
            final_msgs.append(msg)
            added.update(extract_rfc2822_addresses(email_to_header)[0])
            added.update(extract_rfc2822_addresses(email_cc_header)[0])
            break  # Only one message needed for To+Cc

        # Step 2: Send to each BCC individually with correct headers
        for bcc_email in bcc_emails:
            if not bcc_email or bcc_email in added:
                continue

            for msg in res:
                bcc_msg = msg.copy()
                bcc_msg.update({
                    "email_to": bcc_email,  # This ensures actual delivery
                    "email_cc": email_cc_header,  # Show real CC
                    "email_bcc": False,  # Hide BCC
                    "headers": {
                        'To': email_to_header,
                        'Cc': email_cc_header,
                    },
                    "body": (
                        "<p style='color:gray; font-style:italic;'>🔒 You received this email as a BCC (Blind Carbon Copy). "
                        "Please do not reply.</p>"
                        + msg.get("body", "")
                    ),
                })
                final_msgs.append(bcc_msg)
                added.add(bcc_email)
                break

        return final_msgs
