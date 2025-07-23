from odoo import fields, models, tools
from odoo.addons.base.models.ir_mail_server import extract_rfc2822_addresses
import logging

_logger = logging.getLogger(__name__)


def format_emails(partners):
    emails = [
        tools.formataddr((p.name or "", tools.email_normalize(p.email)))
        for p in partners
        if p.email
    ]
    return ", ".join(emails)


def format_emails_raw(partners):
    emails = [p.email for p in partners if p.email]
    return ", ".join(emails)


class MailMail(models.Model):
    _inherit = "mail.mail"

    email_bcc = fields.Char("Bcc", help="Blind Cc message recipients")

    def _prepare_outgoing_list(self, recipients_follower_status=None):
        res = super()._prepare_outgoing_list(recipients_follower_status=recipients_follower_status)
        is_out_of_scope = len(self.ids) > 1
        is_from_composer = self.env.context.get("is_from_composer", False)

        if is_out_of_scope or not is_from_composer:
            return res

        mail = self[0]

        # Build the To, CC, and BCC lists
        partners_cc_bcc = mail.recipient_cc_ids + mail.recipient_bcc_ids
        partner_to_ids = [r.id for r in mail.recipient_ids if r not in partners_cc_bcc]
        partner_to = self.env["res.partner"].browse(partner_to_ids)

        email_to = format_emails(partner_to)
        email_to_raw = format_emails_raw(partner_to)
        email_cc = format_emails(mail.recipient_cc_ids)

        # Filter out BCC from original recipients
        filtered_recipient_ids = [
            r.id for r in mail.recipient_ids if r not in mail.recipient_bcc_ids
        ]

        # Extract body from base message safely
        base_msg = res[0] if res else {}
        original_body = base_msg.get("body", "")

        # Message to To + CC only (no BCCs, no BCC notice)
        clean_msg = base_msg.copy()
        clean_msg.update({
            "email_to": email_to,
            "email_to_raw": email_to_raw,
            "email_cc": email_cc,
            "email_bcc": "",
            "body": original_body,  # Important: no BCC note here
            "recipient_ids": [(6, 0, filtered_recipient_ids)],
        })

        result = [clean_msg]

        # Send one individual mail per BCC recipient
        for partner in mail.recipient_bcc_ids:
            if not partner.email:
                continue

            bcc_email = tools.email_normalize(partner.email)

            # Create a fresh copy of the message
            bcc_msg = base_msg.copy()

            # Headers
            bcc_msg["headers"] = bcc_msg.get("headers", {})
            bcc_msg["headers"].update({"X-Odoo-Bcc": bcc_email})

            # Add BCC notice to the body
            bcc_note = (
                "<p style='color:gray; font-size:small;'>"
                "🔒 You received this email as a BCC (Blind Carbon Copy). "
                "Please do not reply to all.</p>"
            )
            bcc_msg["body"] = bcc_note + original_body

            # Use original To/CC headers, but send only to this BCC
            bcc_msg["email_to"] = email_to_raw
            bcc_msg["email_cc"] = email_cc
            bcc_msg["email_bcc"] = ""
            bcc_msg["recipient_ids"] = [(6, 0, [partner.id])]

            result.append(bcc_msg)

        return result
