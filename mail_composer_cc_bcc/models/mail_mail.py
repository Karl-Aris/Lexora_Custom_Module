# Copyright 2023 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


def format_emails(partners):
    """Convert a recordset of res.partner into email strings."""
    return ', '.join(p.email for p in partners if p.email) if partners else ''


class MailMail(models.Model):
    _inherit = "mail.mail"

    email_bcc = fields.Char("Bcc", help="Blind carbon copy recipients")
    email_cc = fields.Char("Cc", help="Carbon copy recipients")

    @api.model
    def create(self, values):
        if values.get("recipient_cc_ids"):
            partners_cc = self.env["res.partner"].browse(values["recipient_cc_ids"][0][2])
            values["email_cc"] = format_emails(partners_cc)

        if values.get("recipient_bcc_ids"):
            partners_bcc = self.env["res.partner"].browse(values["recipient_bcc_ids"][0][2])
            values["email_bcc"] = format_emails(partners_bcc)

        return super().create(values)
