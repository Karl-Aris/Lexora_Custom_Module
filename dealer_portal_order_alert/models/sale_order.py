from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        order = super().create(vals)

        # Send email if order is placed by a portal user
        if order.user_id and order.user_id.has_group('base.group_portal'):
            template = self.env.ref('dealer_portal_order_alert.email_template_portal_order_confirmation')
            if template:
                template.send_mail(order.id, force_send=True)

        return order