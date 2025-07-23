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

        # Categorize recipients
        recipient_to = mail.recipient_ids - mail.recipient_cc_ids - mail.recipient_bcc_ids
        recipient_cc = mail.recipient_cc_ids
        recipient_bcc = mail.recipient_bcc_ids

        email_to = format_emails(recipient_to)
        email_cc = format_emails(recipient_cc)
        bcc_emails = [tools.email_normalize(p.email) for p in recipient_bcc if p.email]

        final_msgs = []

        # Grab the base message structure (the first item)
        base_msg = res[0].copy()
        original_body = base_msg.get("body", "")

        # Send to visible recipients (To + Cc)
        if email_to or email_cc:
            base_msg.update({
                "email_to": email_to,
                "email_cc": email_cc,
                "email_bcc": "",  # No Bcc in headers
            })
            final_msgs.append(base_msg)

        # Send separate messages to each Bcc recipient
        for bcc_email in bcc_emails:
            bcc_msg = base_msg.copy()
            bcc_msg.update({
                "email_to": bcc_email,
                "email_cc": email_cc,
                "email_bcc": "",  # Still hide Bcc header
                "body": (
                    "<p style='color:gray; font-style:italic;'>🔒 You received this email as a BCC (Blind Carbon Copy). "
                    "Please do not reply to all.</p>" + original_body
                ),
            })
            final_msgs.append(bcc_msg)

        return final_msgs
