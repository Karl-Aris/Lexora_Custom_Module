from odoo import http
from odoo.http import request

class ProductConfigurationController(http.Controller):

    @http.route(['/store/cabinet'], type='http', auth='public', website=True)
    def search_by_sku(self, sku=None, **kwargs):
        product = None
        related_sizes = []
        collection_tag = ''

        if sku:
            product = request.env['product.product'].sudo().search([('default_code', '=', sku)], limit=1)

            if product:
                template = product.product_tmpl_id
                tag_names = template.product_tag_ids.mapped('name')

                # Extract collection tag: the first non-numeric tag NOT in exclusion list
                filter_out = ['Single', 'Vanity Only', 'Bathroom Vanities']
                collection_tag = next((tag for tag in tag_names if not tag.isdigit() and tag not in filter_out), None)

                if collection_tag:
                    collection_tag_rec = request.env['product.tag'].sudo().search([('name', '=', collection_tag)], limit=1)

                    # Required filtering tags
                    filter_tag_names = ['Single', 'Vanity Only', 'Bathroom Vanities']
                    filter_tags = request.env['product.tag'].sudo().search([('name', 'in', filter_tag_names)])

                    # Search product templates that:
                    # - Have the same collection tag
                    # - AND have at least one of the required tags
                    matching_templates = request.env['product.template'].sudo().search([
                        ('product_tag_ids', 'in', collection_tag_rec.id),
                        ('product_tag_ids', 'in', filter_tags.ids),
                    ])

                    # Get all variants of those templates
                    related_sizes = request.env['product.product'].sudo().search([
                        ('product_tmpl_id', 'in', matching_templates.ids)
                    ])

        return request.render('product_configuration.template_product_configuration', {
            'product': product,
            'related_sizes': related_sizes,
            'collection_name': collection_tag,
        })
