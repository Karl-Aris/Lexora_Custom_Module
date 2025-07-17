from odoo import models, fields

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    bcc_partner_ids = fields.Many2many(
        'res.partner',
        'helpdesk_ticket_bcc_partner_rel',
        'ticket_id',
        'partner_id',
        string='BCC Partners'
    )

    def message_post(self, **kwargs):
        bcc_emails = [p.email for p in self.bcc_partner_ids if p.email]
        bcc_partners = self.bcc_partner_ids
    
        if kwargs.get('message_type') == 'email':
            email_values = kwargs.get('email_values', {})
            existing_bcc = email_values.get('bcc', '')
            combined_bcc = list(set(filter(None, existing_bcc.split(',') + bcc_emails)))
            email_values['bcc'] = ','.join(combined_bcc)
            kwargs['email_values'] = email_values
    
        # Inject bcc_partner_ids into message record
        kwargs.setdefault('bcc_partner_ids', [(6, 0, bcc_partners.ids)])
    
        return super(HelpdeskTicket, self).message_post(**kwargs)
