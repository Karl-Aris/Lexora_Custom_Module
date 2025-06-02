from odoo import http
from odoo.http import request
from odoo.addons.payment.models.transaction import PaymentTransaction

class WebsiteSaleAuthorizePatch(http.Controller):

    @http.route(['/shop/shipping/validate'], type='http', auth="user", website=True, sitemap=False)
    def order_finalize_validate(self, **kw):
        order = request.website.sale_get_order()
        if order and kw:
            order.write({
                "state": "to_add_shipment",
                "order_customer": kw.get("order_customer"),
                "order_address": kw.get("order_address"),
                "order_phone": kw.get("order_phone"),
            })

            acquirer = request.env['payment.acquirer'].sudo().search([('provider', '=', 'authorize')], limit=1)
            if acquirer:
                tx_vals = {
                    'acquirer_id': acquirer.id,
                    'amount': order.amount_total,
                    'currency_id': order.currency_id.id,
                    'reference': order.name,
                    'partner_id': order.partner_id.id,
                    'sale_order_ids': [(6, 0, [order.id])],
                }
                tx = request.env['payment.transaction'].sudo().create(tx_vals)
                tx._set_done()
                order.write({'payment_transaction_id': tx.id})
                order.action_confirm()
                request.website.sale_reset()
                return request.render("website_sale_lexora.order_complete_thank_you")

        return http.request.redirect("/shop/checkout")