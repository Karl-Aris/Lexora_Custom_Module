from odoo import http
from odoo.http import request
from werkzeug.utils import redirect
from werkzeug.exceptions import Forbidden


class WebsiteSaleLexora(http.Controller):

    @http.route(['/shop/shipping/validate'], type='http', methods=['POST'], auth="user", website=True, sitemap=False)
    def order_finalize_validate(self, **kw):
        order = request.website.sale_get_order()

        if order and kw:
            order.sudo().write({
                'purchase_order': kw.get("purchase_order"),        # PO #
                'order_customer': kw.get("order_customer"),        # Custom Field
                'order_address': kw.get("order_address"),          # Custom Field
                'order_phone': kw.get("order_phone"),              # Custom Field
                'x_payment_method': kw.get("x_payment_method"),    # Optional Custom Field
            })
            request.website.sale_reset()
            return request.render("website_sale_lexora.order_complete_thank_you")

        return Forbidden()
