from odoo import models, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    def message_post(self, **kwargs):
        self.ensure_one()

        user = self.env.user
        # Change this XML ID to your actual customer service group
        customer_service_group = self.env.ref('base.group_user')  # Example: Internal Users group
        is_customer_service = customer_service_group in user.groups_id

        if is_customer_service:
            # BCC emails of Ilia and Owner - replace with real emails or fetch dynamically
            bcc_emails = ['ilia@example.com', 'owner@example.com']

            email_values = kwargs.get('email_values', {}) or {}

            # Add or append BCC emails
            existing_bcc = email_values.get('email_bcc')
            if existing_bcc:
                bcc_emails = list(set(bcc_emails + existing_bcc.split(',')))

            email_values['email_bcc'] = ','.join(bcc_emails)
            kwargs['email_values'] = email_values

        return super().message_post(**kwargs)
