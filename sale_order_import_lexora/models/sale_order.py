from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    mode_freight = fields.Selection(selection=[
        ('mode', 'Mode'), ('freightview', 'Freightview')
    ], string="Mode/ Freightview")
    order_customer = fields.Char()
    order_address = fields.Char()
    order_phone = fields.Char()

    def create_invoice_register_payment(self):
        for rec in self:
            adv_inv_payment = self.env['sale.advance.payment.inv']
            adv_inv_payment = adv_inv_payment.create({"sale_order_ids": [(6, 0, rec.ids)]})
            adv_inv_payment.create_invoices()
            move_ids = rec.invoice_ids
            move_ids.action_post()

            if sum(move_ids.mapped("invoice_line_ids").mapped("price_unit")) > 0:
                self.env['account.payment.register'].with_context(
                    active_model='account.move',
                    active_ids=move_ids.ids
                ).create({'payment_date': rec.order_process_date})._create_payments()

    def action_open_delivery_wizard(self):
        res = super().action_open_delivery_wizard()
        res['context']['default_mode_freight'] = self.mode_freight

        return res