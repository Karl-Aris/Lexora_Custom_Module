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

        display_to = format_emails(recipient_to)
        display_cc = format_emails(recipient_cc)
        bcc_emails = [tools.email_normalize(p.email) for p in recipient_bcc if p.email]

        final_msgs = []

        seen_recipients = set(bcc_emails)

        # 1. Send the base message to To + Cc ONLY (exclude Bcc completely)
        for msg in res:
            # Parse real To address from the generated message
            extract_result = extract_rfc2822_addresses(msg.get("email_to", ""))
            msg_to_emails = extract_result[0] if extract_result else []

            if any(tools.email_normalize(e) in seen_recipients for e in msg_to_emails):
                continue  # skip if accidentally picking a BCC

            msg.update({
                "email_to": display_to,
                "email_cc": display_cc,
                "email_bcc": "",  # Important: don't Bcc anyone in the base message
            })
            final_msgs.append(msg)
            break  # only one base message

        # 2. Send custom message per Bcc recipient
        for bcc_email in bcc_emails:
            if not bcc_email:
                continue

            partner = self.env['res.partner'].search([('email', '=', bcc_email)], limit=1)

            # Create individual message
            bcc_msg = res[0].copy()
            bcc_msg.update({
                "email_to": display_to,
                "email_cc": display_cc,
                "email_bcc": "",  # Must be blank to avoid "too many To headers" error
                "body": (
                    "<p style='color:gray; font-style:italic;'>🔒 You received this email as a BCC (Blind Carbon Copy). "
                    "Please do not reply to all.</p>" + bcc_msg.get("body", "")
                ),
                "recipient_ids": [(6, 0, [partner.id])] if partner else [],
            })
            final_msgs.append(bcc_msg)

        return final_msgs
