from odoo import models, fields, api
from datetime import date

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Canonical fields (use edd because some views reference 'edd')
    tracking_number = fields.Char(string='Tracking Number', copy=False)
    edd = fields.Date(string='Estimated Delivery Date (EDD)', index=True, copy=False)
    delivery_status = fields.Selection(
        selection=[
            ('shipped', 'Shipped'),
            ('in_transit', 'In Transit'),
            ('delivered', 'Delivered'),
            ('not_delivered_on_edd', 'Not Delivered on EDD'),
            ('exception', 'Exception'),
        ],
        string='Delivery Status',
        default='shipped',
        tracking=True,
        copy=False,
        index=True,
    )
    follow_up_status = fields.Selection(
        selection=[('pending', 'Pending'), ('done', 'Done')],
        string='Follow-up Status',
        default=False,
        copy=False,
        index=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        # Ensure newly-created SOs that have a tracking number default to shipped
        records = super().create(vals_list)
        for rec, vals in zip(records, vals_list):
            if vals.get('tracking_number') and not vals.get('delivery_status') and not rec.delivery_status:
                rec.delivery_status = 'shipped'
        return records

    def write(self, vals):
        # If tracking number was added and no delivery_status set, default to shipped
        res = super().write(vals)
        if 'tracking_number' in vals:
            for rec in self:
                if rec.tracking_number and not rec.delivery_status:
                    rec.delivery_status = 'shipped'
        # If delivery_status changed to delivered, ensure follow up is pending unless already set
        if 'delivery_status' in vals and vals.get('delivery_status') == 'delivered':
            for rec in self:
                if not rec.follow_up_status:
                    rec.follow_up_status = 'pending'
        return res

    @api.model
    def cron_autobucket_missed_edd(self):
        """Daily cron:
        Orders with delivery_status = shipped and edd <= today -> not_delivered_on_edd
        """
        today = date.today()
        domain = [
            ('delivery_status', '=', 'shipped'),
            ('edd', '!=', False),
            ('edd', '<=', today),
        ]
        orders = self.sudo().search(domain)
        for order in orders:
            old = order.delivery_status
            order.sudo().write({'delivery_status': 'not_delivered_on_edd'})
            order.message_post(body=f"Auto-updated delivery_status: {old} → not_delivered_on_edd (EDD {order.edd} passed)")
