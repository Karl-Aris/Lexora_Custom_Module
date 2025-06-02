
from odoo import http
from odoo.http import request
from odoo.fields import Command
from odoo.addons.website_sale.controllers.main import WebsiteSale
from werkzeug.exceptions import Forbidden

class WebsiteSaleAuthorizePatch(WebsiteSale):

    @http.route(['/shop/shipping/validate'], type='http', methods=['GET', 'POST'], auth="user", website=True, sitemap=False)
    def order_finalize_validate(self, **kw):
        order = request.website.sale_get_order()
        if order and kw:
            order.write({
                "state": "to_add_shipment",
                "order_customer": kw.get("order_customer"),
                "order_address": kw.get("order_address"),
                "order_phone": kw.get("order_phone"),
            })

            # Simulate Authorize.Net transaction creation
            acquirer = request.env['payment.acquirer'].sudo().search([
                ('provider', 'in', ['authorize', 'authorize_net']),
                ('state', '=', 'enabled')
            ], limit=1)

            if acquirer:
                tx_vals = {
                    'amount': order.amount_total,
                    'currency_id': order.currency_id.id,
                    'acquirer_id': acquirer.id,
                    'partner_id': order.partner_id.id,
                    'reference': order.name,
                    'sale_order_ids': [Command.set([order.id])],
                }
                tx = request.env['payment.transaction'].sudo().create(tx_vals)
                tx._set_done()

                order.action_confirm()

            request.website.sale_reset()
            return request.render("website_sale_lexora.order_complete_thank_you")

        return Forbidden()
