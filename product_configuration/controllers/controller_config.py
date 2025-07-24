from odoo import http
from odoo.http import request

class ProductConfigurationController(http.Controller):

    @http.route(['/store/cabinet'], type='http', auth='public', website=True)
    def search_by_sku(self, sku=None, **kwargs):
        product = None
        related_sizes = []

        if sku:
            product = request.env['product.product'].sudo().search([('default_code', '=', sku)], limit=1)

            if product:
                template = product.product_tmpl_id
                tag_names = template.product_tag_ids.mapped('name')

                # Extract collection tag (first non-numeric tag)
                collection_tag = next((tag for tag in tag_names if not tag.isdigit()), None)

                if collection_tag:
                    # Search other templates with the same collection tag
                    collection_tag_rec = request.env['product.tag'].sudo().search([('name', '=', collection_tag)], limit=1)

                    matching_templates = request.env['product.template'].sudo().search([
                        ('product_tag_ids', 'in', collection_tag_rec.id)
                    ])

                    related_sizes = request.env['product.product'].sudo().search([
                        ('product_tmpl_id', 'in', matching_templates.ids)
                    ])

        return request.render('product_configuration.template_product_configuration', {
            'product': product,
            'related_sizes': related_sizes,
            'collection_name': collection_tag if product else '',
        })
