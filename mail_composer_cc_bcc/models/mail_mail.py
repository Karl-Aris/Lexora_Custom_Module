# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, tools


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
        res = super()._prepare_outgoing_list(
            recipients_follower_status=recipients_follower_status
        )
        is_out_of_scope = len(self.ids) > 1
        is_from_composer = self.env.context.get("is_from_composer", False)
    
        if is_out_of_scope or not is_from_composer:
            return res
    
        # Collect recipient groups
        partner_to_ids = [p.id for p in self.recipient_ids if p not in self.recipient_cc_ids + self.recipient_bcc_ids]
        partner_to = self.env["res.partner"].browse(partner_to_ids)
        email_to = format_emails(partner_to)
        email_to_raw = format_emails_raw(partner_to)
        email_cc = format_emails(self.recipient_cc_ids)
        bcc_emails = [p.email for p in self.recipient_bcc_ids if p.email]
    
        warning_html = (
            '<div style="color: red; font-weight: bold; margin-bottom: 10px;">'
            '⚠️ You received this message as a BCC recipient. Please do not reply.'
            '</div>'
        )
    
        for m in res:
            rcpt_to = m.get("recipient") or ""
            if any(bcc in rcpt_to for bcc in bcc_emails):
                # Still a BCC, but inject visible notice in body
                if m.get("body") and warning_html not in m["body"]:
                    m["body"] = warning_html + m["body"]
                    m["body_html"] = m["body"]
    
            m.update({
                "email_to": email_to,
                "email_to_raw": email_to_raw,
                "email_cc": email_cc,
            })
    
        return res
