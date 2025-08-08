from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleAuthorizeNetFee(WebsiteSale):

    @http.route(['/shop/payment/transaction'], type='http', auth='public', website=True, csrf=False)
    def shop_payment_transaction(self, **kwargs):
        """
        Override to add Authorize.Net fee before transaction is created.
        """
        order = request.website.sale_get_order()
        if order and order.payment_provider_id and order.payment_provider_id.code == 'authorize':
            fee_product = request.env['product.product'].sudo().search([
                ('default_code', '=', 'AUTH_NET_FEE')
            ], limit=1)

            if fee_product:
                # Remove any previous fee lines
                order.sudo().order_line.filtered(
                    lambda l: l.product_id.id == fee_product.id
                ).unlink()

                # Calculate fee (3.5% of untaxed amount)
                fee_amount = round(order.amount_untaxed * 0.035, 2)
                if fee_amount > 0:
                    request.env['sale.order.line'].sudo().create({
                        'order_id': order.id,
                        'product_id': fee_product.id,
                        'name': fee_product.name,
                        'price_unit': fee_amount,
                        'product_uom_qty': 1,
                    })
                    order.sudo()._amount_all()

        # Continue with normal payment transaction creation
        return super(WebsiteSaleAuthorizeNetFee, self).shop_payment_transaction(**kwargs)
