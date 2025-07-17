from odoo import models, api

class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model_create_multi
    def create(self, vals_list):
        messages = super().create(vals_list)
        tickets = messages.filtered(lambda m: m.model == 'helpdesk.ticket').mapped('res_id')
        self.env['helpdesk.ticket'].browse(tickets)._compute_body_index()
        return messages