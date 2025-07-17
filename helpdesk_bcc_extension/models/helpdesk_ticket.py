from odoo import models, fields


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    bcc_partner_ids = fields.Many2many(
        comodel_name='res.partner',
        relation='helpdesk_ticket_bcc_rel',
        column1='ticket_id',
        column2='partner_id',
        string='BCC Recipients'
    )

    def message_post(self, **kwargs):
        # Remove unsupported key before passing to super
        bcc_partners = kwargs.pop('bcc_partner_ids', False)

        # Call parent method
        message = super().message_post(**kwargs)

        # Handle BCC sending logic separately
        if bcc_partners:
            partners = self.env['res.partner'].browse(bcc_partners)
            bcc_emails = partners.mapped('email')
            if bcc_emails:
                for record in self:
                    self.env['mail.mail'].create({
                        'subject': kwargs.get('subject', f'Re: {record.display_name}'),
                        'body_html': kwargs.get('body', ''),
                        'email_from': self.env.user.email_formatted,
                        'email_to': False,  # Explicitly no "To" email
                        'email_bcc': ','.join(bcc_emails),
                        'model': record._name,
                        'res_id': record.id,
                        'auto_delete': True,
                    }).send()

        return message
