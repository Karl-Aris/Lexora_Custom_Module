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

        email_to = format_emails(recipient_to)
        email_cc = format_emails(recipient_cc)

        bcc_emails = [tools.email_normalize(p.email) for p in recipient_bcc if p.email]
        final_msgs = []

        # 1. Add the main message (To + Cc)
        for msg in res:
            msg.update({
                "email_to": email_to,
                "email_cc": email_cc,
                "email_bcc": "",  # hide bcc
            })
            final_msgs.append(msg)
            break  # only one standard message

        # 2. Add BCC messages separately
        for bcc_email in bcc_emails:
            new_msg = {
                "subject": mail.subject,
                "body": (
                    "<p style='color:gray; font-style:italic;'>🔒 You received this email as a BCC (Blind Carbon Copy). "
                    "Please do not reply-all.</p>"
                    + mail.body
                ),
                "body_html": mail.body,
                "email_from": mail.email_from,
                "email_to": bcc_email,     # set direct recipient
                "email_cc": email_cc,      # visible
                "email_bcc": "",           # hidden
                "reply_to": mail.reply_to,
                "model": mail.model,
                "res_id": mail.res_id,
                "mail_server_id": mail.mail_server_id.id,
                "auto_delete": mail.auto_delete,
                "headers": mail.headers,
                "message_id": tools.generate_tracking_message_id('mail.mail'),
            }
            final_msgs.append(new_msg)

        return final_msgs
