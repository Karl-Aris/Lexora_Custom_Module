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

        is_out_of_scope = len(self.ids) > 1
        is_from_composer = self.env.context.get("is_from_composer", False)

        if is_out_of_scope or not is_from_composer:
            return res

        # Prepare formatted recipients
        partners_cc_bcc = self.recipient_cc_ids + self.recipient_bcc_ids
        partner_to_ids = [r.id for r in self.recipient_ids if r not in partners_cc_bcc]
        partner_to = self.env["res.partner"].browse(partner_to_ids)

        email_to = format_emails(partner_to)
        email_to_list = format_emails_raw(partner_to)
        email_cc = format_emails(self.recipient_cc_ids)
        bcc_emails = [p.email for p in self.recipient_bcc_ids if p.email]

        new_res = []

        # Take first valid mail message as base
        base_msg = res[0] if res else {}
        body_content = base_msg.get("body") or self.body_html or ""

        # -- 1. Add normal TO + CC message
        base_msg.update({
            "email_to": email_to,
            "email_to_raw": ", ".join(email_to_list),
            "email_cc": email_cc,
        })
        new_res.append(base_msg)

        # -- 2. Add one email per BCC
        for bcc_email in bcc_emails:
            bcc_msg = base_msg.copy()
            bcc_msg.update({
                "email_to": bcc_email,
                "email_to_raw": bcc_email,
                "email_cc": "",
                "body": (
                    "<p style='color:gray; font-style:italic;'>"
                    "🔒 You received this email as a BCC (Blind Carbon Copy). Please do not reply."
                    "</p>" + body_content
                ),
            })
            new_res.append(bcc_msg)

        # ✅ THIS IS THE CORRECT WAY: A FLAT LIST OF STRINGS
        recipients_list = email_to_list + bcc_emails

        self.env.context = {
            **self.env.context,
            "recipients": recipients_list,
        }

        _logger.info("TO: %s", email_to_list)
        _logger.info("CC: %s", email_cc)
        _logger.info("BCC: %s", bcc_emails)
        _logger.info("Generated %d outgoing messages", len(new_res))

        return new_res
