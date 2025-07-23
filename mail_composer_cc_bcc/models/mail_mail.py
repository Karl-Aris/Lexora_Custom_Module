# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, tools
from odoo.addons.base.models.ir_mail_server import extract_rfc2822_addresses
import copy


def format_emails(partners):
    return ", ".join([
        tools.formataddr((p.name or "", tools.email_normalize(p.email)))
        for p in partners if p.email
    ])


def format_emails_raw(partners):
    return ", ".join([p.email for p in partners if p.email])


class MailMail(models.Model):
    _inherit = "mail.mail"

    email_bcc = fields.Char("Bcc", help="Blind Cc message recipients")

    def _prepare_outgoing_list(self, recipients_follower_status=None):
        res = super()._prepare_outgoing_list(
            recipients_follower_status=recipients_follower_status
        )

        # Only apply customization for single mail from composer
        if len(self.ids) != 1 or not self.env.context.get("is_from_composer"):
            return res

        mail = self[0]
        recipient_to = mail.recipient_ids - mail.recipient_cc_ids - mail.recipient_bcc_ids
        recipient_cc = mail.recipient_cc_ids
        recipient_bcc = mail.recipient_bcc_ids

        email_to = format_emails(recipient_to)
        email_to_raw = format_emails_raw(recipient_to)
        email_cc = format_emails(recipient_cc)
        email_bcc = [tools.email_normalize(p.email) for p in recipient_bcc if p.email]

        result = []

        # Step 1: One message to To + Cc (no Bcc, no note)
        base_msg = res[0].copy()
        base_msg.update({
            "email_to": email_to,
            "email_to_raw": email_to_raw,
            "email_cc": email_cc,
            "email_bcc": "",  # Don't include actual Bcc header here
        })
        result.append(base_msg)

        # Step 2: One message per Bcc recipient with body note
        for partner in recipient_bcc:
            if not partner.email:
                continue

            bcc_msg = copy.deepcopy(res[0])
            bcc_msg.update({
                "email_to": email_to,
                "email_to_raw": email_to_raw,
                "email_cc": email_cc,
                "email_bcc": "",  # Avoid Bcc header
                "recipient_ids": [(6, 0, [partner.id])],
            })

            # Inject Bcc note into body
            note = (
                "<p style='color:gray; font-style:italic;'>"
                "🔒 You received this email as a BCC (Blind Carbon Copy). "
                "Please do not reply to all.</p>"
            )
            bcc_msg["body"] = note + bcc_msg.get("body", "")
            if "body_html" in bcc_msg:
                bcc_msg["body_html"] = note + bcc_msg.get("body_html", "")

            # Add X-Odoo-Bcc header
            bcc_msg["headers"] = bcc_msg.get("headers", {})
            bcc_msg["headers"].update({"X-Odoo-Bcc": partner.email})

            result.append(bcc_msg)

        return result
