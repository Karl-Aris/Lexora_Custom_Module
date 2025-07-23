from odoo import models, fields, tools
from odoo.addons.base.models.ir_mail_server import extract_rfc2822_addresses
import logging

_logger = logging.getLogger(__name__)

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

        email_to = format_emails(recipient_to)
        email_cc = format_emails(recipient_cc)
        bcc_emails = [tools.email_normalize(p.email) for p in recipient_bcc if p.email]

        final_msgs = []
        seen_recipients = set()

        # Add the standard message with To + Cc
        for msg in res:
            if not isinstance(msg, dict):
                _logger.warning("Skipped non-dict msg: %s", msg)
                continue

            to_emails = extract_rfc2822_addresses(msg.get("email_to", ""))[0]
            if not to_emails:
                continue

            recipient_email = tools.email_normalize(to_emails[0])
            if not recipient_email or recipient_email in bcc_emails or recipient_email in seen_recipients:
                continue

            msg.update({
                "email_to": email_to,
                "email_cc": email_cc,
                "email_bcc": False,
            })

            final_msgs.append(msg)
            seen_recipients.update(extract_rfc2822_addresses(email_to)[0])
            seen_recipients.update(extract_rfc2822_addresses(email_cc)[0])
            break  # Only send one main message

        # Add separate BCC messages
        for bcc_email in bcc_emails:
            if bcc_email in seen_recipients:
                continue

            for base_msg in res:
                if not isinstance(base_msg, dict):
                    continue

                bcc_msg = base_msg.copy()
                bcc_msg.update({
                    "email_to": bcc_email,
                    "email_cc": "",
                    "email_bcc": "",
                    "body": (
                        "<p style='color:gray; font-style:italic;'>🔒 You received this email as a BCC (Blind Carbon Copy). "
                        "Please do not reply.</p>" + base_msg.get("body", "")
                    ),
                })

                final_msgs.append(bcc_msg)
                seen_recipients.add(bcc_email)
                break

        return final_msgs
