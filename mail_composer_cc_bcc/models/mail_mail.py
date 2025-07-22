from odoo import fields, models, tools
from odoo.addons.base.models.ir_mail_server import extract_rfc2822_addresses
import logging

_logger = logging.getLogger(__name__)


def format_emails(partners):
    return ", ".join([
        tools.formataddr((p.name or "", tools.email_normalize(p.email)))
        for p in partners if p.email
    ])


def format_emails_raw(partners):
    return [p.email for p in partners if p.email]


class MailMail(models.Model):
    _inherit = "mail.mail"

    email_bcc = fields.Char("Bcc", help="Blind Cc message recipients")

    def _prepare_outgoing_list(self, recipients_follower_status=None):
        res = super()._prepare_outgoing_list(recipients_follower_status=recipients_follower_status)

        # Only apply to single mail, and only when composing manually
        if len(self.ids) > 1 or not self.env.context.get("is_from_composer", False):
            return res

        partners_cc_bcc = self.recipient_cc_ids + self.recipient_bcc_ids
        partner_to_ids = [r.id for r in self.recipient_ids if r not in partners_cc_bcc]
        partner_to = self.env["res.partner"].browse(partner_to_ids)

        email_to = format_emails(partner_to)
        email_to_raw = format_emails_raw(partner_to)
        email_cc = format_emails(self.recipient_cc_ids)
        email_cc_raw = format_emails_raw(self.recipient_cc_ids)
        bcc_emails = [p.email for p in self.recipient_bcc_ids if p.email]

        new_res = []
        base_msg = res[0] if res else {}
        body_content = base_msg.get("body") or self.body_html or ""

        # 1. Main message: TO and CC only
        to_msg = base_msg.copy()
        to_msg.update({
            "email_to": email_to,
            "email_cc": email_cc,
            "email_bcc": "",  # explicitly clear bcc
            "body": body_content,
        })
        new_res.append(to_msg)

        # 2. One separate message per BCC recipient
        for bcc_email in bcc_emails:
            bcc_msg = base_msg.copy()
            bcc_msg.update({
                "email_to": bcc_email,
                "email_cc": "",
                "email_bcc": "",
                "body": (
                    "<p style='color:gray; font-style:italic;'>"
                    "🔒 You received this email as a BCC (Blind Carbon Copy). Please do not reply.</p>"
                    + body_content
                ),
            })
            new_res.append(bcc_msg)

        # Update recipients list for SMTP (TO + CC + BCC)
        self.env.context = {
            **self.env.context,
            "recipients": email_to_raw + email_cc_raw + bcc_emails,
        }

        _logger.info("Prepared Mail - TO: %s", email_to_raw)
        _logger.info("Prepared Mail - CC: %s", email_cc_raw)
        _logger.info("Prepared Mail - BCC: %s", bcc_emails)

        return new_res
