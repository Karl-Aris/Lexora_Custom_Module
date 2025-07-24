from odoo import http
from odoo.http import request

class ProductConfigurationController(http.Controller):

    @http.route(['/store/cabinet'], type='http', auth='public', website=True)
    def search_by_sku(self, sku=None, **kwargs):
        product = None
        related_sizes = []
        collection_tag = ''
        color_tag = ''

        if sku:
            # Get the product by SKU
            product = request.env['product.product'].sudo().search([('default_code', '=', sku)], limit=1)

            if product:
                template = product.product_tmpl_id
                tag_names = template.product_tag_ids.mapped('name')

                # Define known tags that are NOT collection or color
                excluded_tags = ['Vanity Only', 'Bathroom Vanities', 'Single', 'Double', 'Top', 'Sink']
                fixed_tags = ['Vanity Only', 'Bathroom Vanities']

                # Find collection tag (first non-numeric tag not in excluded list)
                collection_tag = next((tag for tag in tag_names if not tag.isdigit() and tag not in excluded_tags), None)

                # Find color tag (another non-numeric tag not in fixed/excluded list and not collection)
                excluded_tags_for_color = excluded_tags + [collection_tag]
                color_tag = next(
                    (tag for tag in tag_names if not tag.isdigit() and tag not in excluded_tags_for_color),
                    None
                )

                if collection_tag and color_tag:
                    # Prepare full list of required tags
                    required_tag_names = fixed_tags + [collection_tag, color_tag]

                    # Fetch those tag records
                    tag_recs = request.env['product.tag'].sudo().search([('name', 'in', required_tag_names)])

                    if len(tag_recs) == 4:
                        required_tag_ids = set(tag_recs.ids)

                        # Search all product templates
                        matching_templates = request.env['product.template'].sudo().search([])

                        # Filter templates that have *all required tags*
                        matching_templates = matching_templates.filtered(
                            lambda tmpl: required_tag_ids.issubset(set(tmpl.product_tag_ids.ids))
                        )

                        # Get variants from those templates
                        related_sizes = request.env['product.product'].sudo().search([
                            ('product_tmpl_id', 'in', matching_templates.ids)
                        ])

        return request.render('product_configuration.template_product_configuration', {
            'product': product,
            'related_sizes': related_sizes,
            'collection_name': collection_tag,
            'color_name': color_tag,
        })
