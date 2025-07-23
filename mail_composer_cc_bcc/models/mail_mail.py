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

        # Only apply custom logic when called from composer
        if len(self.ids) != 1 or not self.env.context.get("is_from_composer"):
            return res

        mail = self[0]
        recipient_to = mail.recipient_ids - mail.recipient_cc_ids - mail.recipient_bcc_ids
        recipient_cc = mail.recipient_cc_ids
        recipient_bcc = mail.recipient_bcc_ids

        email_to = format_emails(recipient_to)
        email_cc = format_emails(recipient_cc)
        bcc_emails = [tools.email_normalize(p.email) for p in recipient_bcc if p.email]

        final_msgs = []
        seen_recipients = set()

        # Add normal message (To + CC)
        for msg in res:
            extract_result = extract_rfc2822_addresses(msg.get("email_to", ""))
            if not extract_result or not extract_result[0]:
                continue  # skip empty or invalid "To" email

            recipient_email = tools.email_normalize(extract_result[0][0])
            if recipient_email in bcc_emails or recipient_email in seen_recipients:
                continue  # avoid duplicates

            msg.update({
                "email_to": email_to,
                "email_cc": email_cc,
                "email_bcc": False,  # Ensure Bcc is empty
            })
            final_msgs.append(msg)

            seen_recipients.update([tools.email_normalize(e) for e in extract_rfc2822_addresses(email_to)[0]])
            seen_recipients.update([tools.email_normalize(e) for e in extract_rfc2822_addresses(email_cc)[0]])
            break  # only send one standard message

        # Add individual BCC messages
        bcc_sent = set()
        for bcc_email in bcc_emails:
            if bcc_email in seen_recipients or bcc_email in bcc_sent:
                continue

            for msg in res:
                new_msg = msg.copy()
                new_msg.update({
                    "email_to": email_to,  # keep headers visible to BCC
                    "email_cc": email_cc,
                    "email_bcc": "",  # ensure actual BCC header is not used
                    "recipient_ids": False,  # prevent message from going to others
                    "body": (
                        "<p style='color:gray; font-style:italic;'>🔒 You received this email as a BCC (Blind Carbon Copy). "
                        "Please do not reply all.</p>"
                        + msg.get("body", "")
                    ),
                })
                # Explicitly override actual recipients
                new_msg["recipient_ids"] = [(6, 0, [p.id for p in recipient_bcc if tools.email_normalize(p.email) == bcc_email])]
                final_msgs.append(new_msg)
                bcc_sent.add(bcc_email)
                break

        return final_msgs
