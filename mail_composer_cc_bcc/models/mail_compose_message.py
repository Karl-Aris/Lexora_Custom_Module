from odoo import fields, models, api


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    recipient_cc_ids = fields.Many2many(
        'res.partner', 'mail_compose_message_cc_rel', 'wizard_id', 'partner_id',
        string='CC'
    )

    recipient_bcc_ids = fields.Many2many(
        'res.partner', 'mail_compose_message_bcc_rel', 'wizard_id', 'partner_id',
        string='BCC'
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        self = self.with_context(is_from_composer=True)
        return res

    def get_mail_values(self, res_ids):
        values = super().get_mail_values(res_ids)

        for res_id in res_ids:
            val = values[res_id]

            # Attach CC and BCC partner IDs
            val['recipient_cc_ids'] = [(6, 0, self.recipient_cc_ids.ids)]
            val['recipient_bcc_ids'] = [(6, 0, self.recipient_bcc_ids.ids)]

            # Ensure context flag is passed
            val['context'] = dict(self._context, is_from_composer=True)

        return values
