from odoo import models, api, _

class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def message_route(self, message, message_dict, model=None, thread_id=None, custom_values=None):
        routes = super().message_route(message, message_dict, model, thread_id, custom_values)

        # Check if the incoming message is a reply to a sale.order
        if model == 'sale.order' or (not model and 'sale.order' in message_dict.get('references', '')):
            author_email = message_dict.get('email_from')
            subject = message_dict.get('subject')
            body = message_dict.get('body')

            # Create a Helpdesk Ticket
            team = self.env['helpdesk.team'].search([], limit=1)  # Assign the default team
            self.env['helpdesk.ticket'].create({
                'name': f"Reply from {author_email}: {subject}",
                'description': body,
                'email': author_email,
                'team_id': team.id if team else False,
            })

        return routes
