from odoo import http
from odoo.http import request


class ProductConfigurationController(http.Controller):

    @http.route(['/store'], type='http', auth='public', website=True)
    def render_product(self, **kwargs):
        return request.render('product_configuration.template_product_configuration')

    @http.route(['/store/cabinet'], type='http', auth='public', website=True)
    def search_by_sku(self, sku=None, **kwargs):
        product = None
        related_sizes = []
        related_countertops = []
        collection_tag = ''
        color_tag = ''

        if sku:
            product = request.env['product.product'].sudo().search([
                ('default_code', '=', sku)
            ], limit=1)

            if product:
                template = product.product_tmpl_id
                tag_names = template.product_tag_ids.mapped('name')

                # Determine collection (non-numeric, not one of the fixed tags)
                fixed_tags = ['Vanity Only', 'Bathroom Vanities', 'Countertops', 'Top', 'Sink']
                collection_tag = next(
                    (tag for tag in tag_names if not tag.isdigit() and tag not in fixed_tags),
                    None
                )

                # Determine color (another tag not digit and not in excluded + not collection)
                excluded_for_color = fixed_tags + [collection_tag]
                color_tag = next(
                    (tag for tag in tag_names if not tag.isdigit() and tag not in excluded_for_color),
                    None
                )

                # ---------- Related Sizes ----------
                if collection_tag and color_tag:
                    size_required_tags = request.env['product.tag'].sudo().search([
                        ('name', 'in', ['Vanity Only', 'Bathroom Vanities', collection_tag, color_tag])
                    ])
                    if len(size_required_tags) == 4:
                        size_templates = request.env['product.template'].sudo().search([])
                        size_templates = size_templates.filtered(
                            lambda tmpl: set(size_required_tags.ids).issubset(set(tmpl.product_tag_ids.ids))
                        )
                        related_sizes = request.env['product.product'].sudo().search([
                            ('product_tmpl_id', 'in', size_templates.ids)
                        ])

                # ---------- Related Countertops ----------
                if collection_tag:
                    countertop_required_tags = request.env['product.tag'].sudo().search([
                        ('name', 'in', ['Countertops', collection_tag])
                    ])
                    if len(countertop_required_tags) == 2:
                        countertop_templates = request.env['product.template'].sudo().search([])
                        countertop_templates = countertop_templates.filtered(
                            lambda tmpl: set(countertop_required_tags.ids).issubset(set(tmpl.product_tag_ids.ids))
                        )
                        related_countertops = request.env['product.product'].sudo().search([
                            ('product_tmpl_id', 'in', countertop_templates.ids)
                        ])

        return request.render('product_configuration.template_product_configuration', {
            'product': product,
            'related_sizes': related_sizes,
            'related_countertops': related_countertops,
            'collection_name': collection_tag,
            'color_name': color_tag,
        })
