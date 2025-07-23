from odoo import models, api


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.model
    def _add_bcc_notice_to_body(self, body):
        notice = (
            "<p style='color:gray; font-size:small;'>"
            "🔒 You received this email as a BCC (Blind Carbon Copy). "
            "Please do not reply to all.</p>"
        )
        return notice + body if body else notice

    def get_mail_values(self, res_ids):
        mail_values = super().get_mail_values(res_ids)
        context = dict(self.env.context)

        # Inject BCC note if the current message is meant for a BCC recipient
        for res_id, values in mail_values.items():
            if context.get("is_bcc_split_for", False):
                values["body"] = self._add_bcc_notice_to_body(values.get("body", ""))

        return mail_values
