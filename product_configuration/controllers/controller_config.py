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
            product = request.env['product.product'].sudo().search([('default_code', '=', sku)], limit=1)

            if product:
                template = product.product_tmpl_id
                tag_names = template.product_tag_ids.mapped('name')

                # Known fixed tags
                fixed_tags = ['Vanity Only', 'Bathroom Vanities']
                numeric_tags = [tag for tag in tag_names if tag.isdigit()]
                
                # Extract collection (non-numeric, not fixed tags)
                collection_tag = next((tag for tag in tag_names if not tag.isdigit() and tag not in fixed_tags), None)

                # Extract color tag (another non-numeric, non-fixed tag ≠ collection)
                color_tag = next(
                    (tag for tag in tag_names if not tag.isdigit() and tag not in fixed_tags and tag != collection_tag),
                    None
                )

                if collection_tag and color_tag:
                    # All required tag names
                    required_tag_names = fixed_tags + [collection_tag, color_tag]

                    # Search for those tag records
                    tag_recs = request.env['product.tag'].sudo().search([('name', 'in', required_tag_names)])

                    if len(tag_recs) == 4:
                        required_tag_ids = set(tag_recs.ids)

                        # Search all product templates (could be optimized further)
                        matching_templates = request.env['product.template'].sudo().search([])

                        # Filter those with ALL required tags
                        matching_templates = matching_templates.filtered(
                            lambda tmpl: required_tag_ids.issubset(set(tmpl.product_tag_ids.ids))
                        )

                        # Get related variants
                        related_sizes = request.env['product.product'].sudo().search([
                            ('product_tmpl_id', 'in', matching_templates.ids)
                        ])

        return request.render('product_configuration.template_product_configuration', {
            'product': product,
            'related_sizes': related_sizes,
            'collection_name': collection_tag,
            'color_name': color_tag,
        })
