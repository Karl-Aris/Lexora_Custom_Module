from odoo import models, api, _
import re

class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def message_route(self, message, message_dict, model=None, thread_id=None, custom_values=None):
        routes = super().message_route(message, message_dict, model, thread_id, custom_values)

        email_to = message_dict.get('to', '').lower()
        subject = message_dict.get('subject', '')
        email_from = message_dict.get('email_from', '')
        body = message_dict.get('body', '')

        # Custom catch: if email sent to catchall/CS and is not linked to thread
        if 'cs@lexorahome.com' in email_to or 'catchall@lexora.net' in email_to:
            # Try to find SO number in subject
            so_match = re.search(r'\bS\d+\b', subject)
            so = None
            if so_match:
                so = self.env['sale.order'].search([('name', '=', so_match.group(0))], limit=1)

            team = self.env['helpdesk.team'].search([], limit=1)

            ticket = self.env['helpdesk.ticket'].create({
                'name': f"Inquiry: {subject or 'No Subject'}",
                'description': body,
                'email': email_from,
                'team_id': team.id if team else False,
            })

            # Optional: log on SO chatter
            if so:
                so.message_post(body=f"Customer replied and a ticket was created: {ticket.name}", message_type="comment")

        return routes
