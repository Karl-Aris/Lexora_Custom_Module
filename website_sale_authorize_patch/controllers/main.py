from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleExtended(WebsiteSale):

    @http.route(['/shop/shipping-details/confirm'], type='http', methods=['POST'], auth="user", website=True)
    def order_finalize(self, **kw):
        try:
            order = request.website.sale_get_order()
            if not order:
                _logger.error("No order found.")
                return request.redirect("/shop")
    
            _logger.info("Order found: %s", order.name)
            _logger.info("POST data: %s", kw)
    
            # Validate and save shipping info
            order.write({
                'order_customer': kw.get('order_customer'),
                'order_address': kw.get('order_address'),
                'order_phone': kw.get('order_phone'),
                'state': 'to_add_shipment',
            })
    
            # Optional: log payment transaction creation
            tx = request.env['payment.transaction'].sudo().create({
                'amount': order.amount_total,
                'currency_id': order.currency_id.id,
                'acquirer_id': request.env['payment.acquirer'].search([('provider', '=', 'authorize')], limit=1).id,
                'partner_id': order.partner_id.id,
                'reference': order.name,
                'sale_order_ids': [(6, 0, [order.id])],
            })
            tx._set_done()
            order.action_confirm()
    
            return request.render("website_sale_lexora.order_complete_thank_you")
    
        except Exception as e:
            _logger.exception("Error finalizing shipping details")
            return request.redirect("/shop")
    
