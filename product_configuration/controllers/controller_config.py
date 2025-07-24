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

                # Define required tags (collection + type filters)
                base_filter_tags = ['Bathroom Vanities', 'Vanity Only']
                # Extract collection tag — must be non-numeric and not in the base list
                collection_tag = next((tag for tag in tag_names if not tag.isdigit() and tag not in base_filter_tags), None)

                if collection_tag:
                    # Get all required tag records
                    all_required_tag_names = base_filter_tags + [collection_tag]
                    tag_recs = request.env['product.tag'].sudo().search([('name', 'in', all_required_tag_names)])

                    if len(tag_recs) == 3:
                        # Find product templates that have *all 3* required tags
                        matching_templates = request.env['product.template'].sudo().search([])

                        # Only keep templates that have all 3 tag IDs
                        required_tag_ids = set(tag_recs.ids)
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
        })
