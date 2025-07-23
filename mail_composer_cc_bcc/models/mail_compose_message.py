from odoo import models, api


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.model
    def _add_bcc_notice_to_body(self, body, bcc_partners):
        if not bcc_partners:
            return body
        notice = (
            "<p style='color:gray;font-size:small;'>"
            "🔒 You received this email as a BCC (Blind Carbon Copy). "
            "Please do not reply to all.</p>"
        )
        return body + notice if body else notice

    def get_mail_values(self, res_ids):
        mail_values = super().get_mail_values(res_ids)
        bcc_partners = self.partner_ids.filtered(lambda p: p.id in self.bcc_partner_ids.ids)

        for res_id, values in mail_values.items():
            if bcc_partners:
                values["body"] = self._add_bcc_notice_to_body(values.get("body", ""), bcc_partners)
        return mail_values
