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
        bcc_partners = [p for p in recipient_bcc if p.email]
        bcc_emails = [tools.email_normalize(p.email) for p in bcc_partners]

        final_msgs = []
        standard_sent = False

        # Send ONE clean email to To + Cc
        for msg in res:
            clean_msg = msg.copy()  # completely isolated
            clean_msg.update({
                "email_to": email_to,
                "email_cc": email_cc,
                "email_bcc": "",  # don't expose BCC
                "body": msg.get("body", ""),  # no BCC note
            })
            final_msgs.append(clean_msg)
            standard_sent = True
            break

        # Send SEPARATE BCC emails
        for partner in bcc_partners:
            bcc_email = tools.email_normalize(partner.email)
            for msg in res:
                bcc_msg = msg.copy()
                bcc_msg.update({
                    "email_to": email_to,
                    "email_cc": email_cc,
                    "email_bcc": "",
                    "headers": {
                        "X-Odoo-Bcc": bcc_email
                    },
                    "body": (
                        "<p style='color:gray; font-style:italic;'>🔒 You received this email as a BCC (Blind Carbon Copy). "
                        "Please do not reply.</p>" + msg.get("body", "")
                    ),
                    "recipient_ids": [(6, 0, [partner.id])],
                })
                final_msgs.append(bcc_msg)
                break

        return final_msgs
