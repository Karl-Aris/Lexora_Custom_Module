from odoo import models, fields, api
from datetime import date

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Fields used by the workflow
    edd = fields.Date(string="Estimated Delivery Date")
    tracking_number = fields.Char(string="Tracking Number", copy=False)
    estimated_delivery_date = fields.Date(string="Estimated Delivery Date", index=True, copy=False)
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

    @api.model
    def cron_autobucket_missed_edd(self):
        """Daily cron: move orders with EDD <= today and status = shipped -> not_delivered_on_edd."""
        today = date.today()
        domain = [
            ('delivery_status', '=', 'shipped'),
            ('estimated_delivery_date', '!=', False),
            ('estimated_delivery_date', '<=', today),
        ]
        orders = self.sudo().search(domain)
        for order in orders:
            old = order.delivery_status
            order.sudo().write({'delivery_status': 'not_delivered_on_edd'})
            # add chatter note
            order.message_post(body=f"Auto-updated delivery_status: {old} → not_delivered_on_edd (EDD passed)")

    # Optional convenience: set shipped when user enters tracking number via write/create
    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        for rec, vals in zip(recs, vals_list):
            if vals.get('tracking_number') and not vals.get('delivery_status'):
                rec.delivery_status = 'shipped'
        return recs

    def write(self, vals):
        # if tracking_number added and delivery_status empty -> set shipped
        res = super().write(vals)
        if 'tracking_number' in vals:
            for rec in self:
                if rec.tracking_number and not rec.delivery_status:
                    rec.delivery_status = 'shipped'
        # when marking delivered, set follow_up_status to pending if unset
        if 'delivery_status' in vals and vals.get('delivery_status') == 'delivered':
            for rec in self:
                if not rec.follow_up_status:
                    rec.follow_up_status = 'pending'
        return res
