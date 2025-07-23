from odoo import models, fields, tools
from odoo.addons.base.models.ir_mail_server import extract_rfc2822_addresses


def format_emails(partners):
    """Format partner records into a properly encoded RFC 2822 email list."""
    return ", ".join([
        tools.formataddr((p.name or "", tools.email_normalize(p.email)))
        for p in partners if p.email
    ])


class MailMail(models.Model):
    _inherit = "mail.mail"

    email_bcc = fields.Char("Bcc", help="Blind Cc message recipients")

    def _prepare_outgoing_list(self, recipients_follower_status=None):
        """Customize outgoing emails: send one regular message, and one per BCC recipient."""
        res = super()._prepare_outgoing_list(recipients_follower_status=recipients_follower_status)

        if len(self.ids) != 1 or not self.env.context.get("is_from_composer"):
            return res

        mail = self[0]
        recipient_to = mail.recipient_ids
        recipient_cc = mail.recipient_cc_ids
        recipient_bcc = mail.recipient_bcc_ids

        # Generate formatted emails
        email_to = format_emails(recipient_to)
        email_cc = format_emails(recipient_cc)
        email_bcc = format_emails(recipient_bcc)

        # Normalize individual BCC addresses for sending separate emails
        bcc_emails = [tools.email_normalize(p.email) for p in recipient_bcc if p.email]

        final_msgs = []
        seen_recipients = set()

        # Prepare the main (To + Cc + Bcc) message — shown to regular recipients
        for msg in res:
            extract_result = extract_rfc2822_addresses(msg.get("email_to", ""))
            msg_to_emails = extract_result[0] if extract_result else []

            if not msg_to_emails:
                continue

            recipient_email = tools.email_normalize(msg_to_emails[0])
            if recipient_email in bcc_emails or recipient_email in seen_recipients:
                continue

            msg.update({
                "email_to": email_to,
                "email_cc": email_cc,
                "email_bcc": email_bcc,
            })

            final_msgs.append(msg)

            # Track seen emails to prevent duplicates
            seen_recipients.update(extract_rfc2822_addresses(email_to)[0])
            seen_recipients.update(extract_rfc2822_addresses(email_cc)[0])
            break  # Only one "To/Cc" message needed

        # Now send individual BCC copies — each gets only their own message
        bcc_sent = set()
        for bcc_email in bcc_emails:
            if bcc_email in seen_recipients or bcc_email in bcc_sent:
                continue

            for msg in res:
                new_msg = msg.copy()
                new_msg.update({
                    "email_to": "",  # Intentionally empty so it's not duplicated in To
                    "email_cc": "",  # No CC for BCC recipients
                    "email_bcc": bcc_email,
                    "body": (
                        "<p style='color:gray; font-style:italic;'>🔒 You received this email as a BCC (Blind Carbon Copy). "
                        "Please do not reply.</p>"
                        + msg.get("body", "")
                    ),
                })
                final_msgs.append(new_msg)
                bcc_sent.add(bcc_email)
                break

        return final_msgs
