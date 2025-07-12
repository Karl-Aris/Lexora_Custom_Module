from odoo import models

class MailTemplate(models.Model):
    _inherit = "mail.template"

    def send_mail(self, res_id, force_send=False, raise_exception=False, email_values=None, *args, **kwargs):
        if email_values is None:
            email_values = {}

        # Check if the template is used for sale.order and override reply_to
        if self.model == 'sale.order':
            email_values['reply_to'] = 'orders@lexorahome.com'

        return super().send_mail(res_id, force_send, raise_exception, email_values=email_values, *args, **kwargs)
