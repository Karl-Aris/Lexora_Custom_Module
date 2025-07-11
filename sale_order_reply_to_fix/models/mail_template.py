from odoo import models

class MailTemplate(models.Model):
    _inherit = "mail.template"

    def send_mail(self, res_id, force_send=False, email_values=None, notif_layout=False):
        if self.model == 'sale.order':
            email_values = email_values or {}
            if 'reply_to' not in email_values:
                order = self.env['sale.order'].browse(res_id)
                email_values['reply_to'] = order.user_id.email or self.env.user.email
        return super().send_mail(res_id, force_send=force_send, email_values=email_values, notif_layout=notif_layout)
