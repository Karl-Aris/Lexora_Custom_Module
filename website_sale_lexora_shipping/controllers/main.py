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
                'purchase_order': kw.get("purchase_order"),       # <-- this is the key field
                'partner_name': kw.get("order_customer"),
                'partner_phone': kw.get("order_phone"),
                'partner_street': kw.get("order_address"),
                'x_payment_method': kw.get("x_payment_method"),   # if this is a valid custom field
            })

            # Optional: reset session or move to thank you page
            request.website.sale_reset()
            return request.render("website_sale_lexora.order_complete_thank_you")

        return Forbidden()
