from odoo import http
from odoo.http import request

class ProductConfigurationController(http.Controller):

    @http.route(['/store/cabinet'], type='http', auth='public', website=True)
def search_by_sku(self, sku=None, **kwargs):
    product = None
    related_sizes = []
    related_countertops = []
    collection_tag = ''
    color_tag = ''

    if sku:
        product = request.env['product.product'].sudo().search([('default_code', '=', sku)], limit=1)

        if product:
            template = product.product_tmpl_id
            tag_names = template.product_tag_ids.mapped('name')

            excluded_tags = ['Vanity Only', 'Bathroom Vanities', 'Single', 'Double', 'Top', 'Sink', 'Countertop']
            fixed_tags = ['Vanity Only', 'Bathroom Vanities']

            # Determine collection and color
            collection_tag = next((tag for tag in tag_names if not tag.isdigit() and tag not in excluded_tags), None)
            excluded_tags_for_color = excluded_tags + [collection_tag]
            color_tag = next(
                (tag for tag in tag_names if not tag.isdigit() and tag not in excluded_tags_for_color),
                None
            )

            if collection_tag and color_tag:
                # Tags for sizes
                size_required_tags = request.env['product.tag'].sudo().search([
                    ('name', 'in', fixed_tags + [collection_tag, color_tag])
                ])

                # Tags for countertops
                countertop_required_tags = request.env['product.tag'].sudo().search([
                    ('name', 'in', ['Countertop', collection_tag, color_tag])
                ])

                # Find size products
                if len(size_required_tags) == 4:
                    matching_templates = request.env['product.template'].sudo().search([])
                    matching_templates = matching_templates.filtered(
                        lambda tmpl: set(size_required_tags.ids).issubset(set(tmpl.product_tag_ids.ids))
                    )
                    related_sizes = request.env['product.product'].sudo().search([
                        ('product_tmpl_id', 'in', matching_templates.ids)
                    ])

                # Find countertop products
                if len(countertop_required_tags) == 3:
                    matching_countertops = request.env['product.template'].sudo().search([])
                    matching_countertops = matching_countertops.filtered(
                        lambda tmpl: set(countertop_required_tags.ids).issubset(set(tmpl.product_tag_ids.ids))
                    )
                    related_countertops = request.env['product.product'].sudo().search([
                        ('product_tmpl_id', 'in', matching_countertops.ids)
                    ])

    return request.render('product_configuration.template_product_configuration', {
        'product': product,
        'related_sizes': related_sizes,
        'related_countertops': related_countertops,
        'collection_name': collection_tag,
        'color_name': color_tag,
    })
