from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleExtended(WebsiteSale):

    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True)
    def confirm_order(self, post):
        order = request.website.sale_get_order()

        # Save the x_payment_method field to sale.order
        if post.get("x_payment_method"):
            order.write({
                'x_payment_method': post.get("x_payment_method")
            })

        # Continue the default behavior
        return super(WebsiteSaleExtended, self).confirm_order(post)
