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

        display_to = format_emails(recipient_to)
        display_cc = format_emails(recipient_cc)
        bcc_emails = [tools.email_normalize(p.email) for p in recipient_bcc if p.email]

        final_msgs = []

        # 1. Standard message to visible recipients
        base_msg = res[0].copy()
        base_msg.update({
            "email_to": display_to,
            "email_cc": display_cc,
            "email_bcc": "",
        })
        final_msgs.append(base_msg)

        # 2. Individual BCC messages
        for bcc_email in bcc_emails:
            if not bcc_email:
                continue

            partner = self.env['res.partner'].search([('email', '=', bcc_email)], limit=1)
            _logger.info("Creating BCC email for %s (partner: %s)", bcc_email, partner.name if partner else "N/A")

            bcc_msg = base_msg.copy()
            bcc_msg.update({
                "email_to": bcc_email,
                "email_cc": "",
                "email_bcc": "",
                "headers": {
                    "To": display_to,
                    "Cc": display_cc,
                },
                "body": (
                    "<p style='color:gray; font-style:italic;'>🔒 You received this email as a BCC (Blind Carbon Copy). "
                    "Please do not reply to all.</p>" + base_msg.get("body", "")
                ),
                "recipient_ids": [(6, 0, [partner.id])] if partner else [],
            })
            final_msgs.append(bcc_msg)

        return final_msgs
