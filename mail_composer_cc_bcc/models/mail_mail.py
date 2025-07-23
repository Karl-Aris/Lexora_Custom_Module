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
        sent_bcc = set()

        # Send normal email to To and Cc (no note)
        for msg in res:
            msg.update({
                "email_to": email_to_header,
                "email_cc": email_cc_header,
                "email_bcc": False,
            })
            final_msgs.append(msg)
            break

        # Send BCC emails (with hidden identity but visible To/Cc headers)
        for bcc_email in bcc_emails:
            if bcc_email in sent_bcc:
                continue

            for msg in res:
                new_msg = msg.copy()
                new_msg.update({
                    "email_to": email_to_header,     # Show original To (for header)
                    "email_cc": email_cc_header,
                    "email_bcc": False,
                    "recipient_ids": False,          # Clear default
                    "body": (
                        "<p style='color:gray; font-style:italic;'>🔒 You received this email as a BCC (Blind Carbon Copy). "
                        "Please do not reply.</p>"
                        + msg.get("body", "")
                    ),
                })

                # Override actual delivery using 'recipient_ids'
                # Force email to deliver to BCC email
                new_msg["email_to_real"] = bcc_email  # Custom key, used in send_email

                final_msgs.append(new_msg)
                sent_bcc.add(bcc_email)
                break

        return final_msgs
