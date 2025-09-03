from odoo import api, fields, models


class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = 'choose.delivery.carrier'

    mode_freight = fields.Selection(selection=[
        ('mode', 'Mode'), ('freightview', 'Freightview')
    ], string="Mode/ Freightview")
    display_price = fields.Float(string='Shipping Quote')
    carrier_tracking_ref = fields.Char(related="order_id.carrier_tracking_ref", readonly=False)
    attachment_ids = fields.Many2many('ir.attachment', related="order_id.attachment_ids", readonly=False)
    dimension = fields.Char(related="order_id.dimension", readonly=False)

    def button_confirm(self):
        self.order_id.write({"mode_freight": self.mode_freight})
        self.order_id._onchange_carrier_id()
        super().button_confirm()
