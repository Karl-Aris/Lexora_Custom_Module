from odoo import http
from odoo.http import request


class ProductConfigurationController(http.Controller):

    @http.route(['/store'], type='http', auth='public', website=True)
    def render_product(self, **kwargs):
        return request.render('product_configuration.template_product_configuration')

    @http.route(['/store/cabinet'], type='http', auth='public', website=True)
    def search_by_sku(self, cabinet_sku=None, counter_top_sku=None, mirror_sku=None, faucet_sku=None, **kwargs):
        product = None
        related_sizes = []
        related_countertops = []
        related_mirrors = []
        related_faucets = []
        collection_tag = ''
        color_tag = ''
        selected_countertop = None
        selected_mirror = None
        selected_faucet = None

        if cabinet_sku:
            kit = request.env['product.kits'].sudo().search([('cabinet_sku', '=', cabinet_sku)], limit=1)

            if kit:
                product = request.env['product.product'].sudo().search([('default_code', '=', kit.cabinet_sku)], limit=1)

                if counter_top_sku:
                    selected_countertop = request.env['product.product'].sudo().search([('default_code', '=', counter_top_sku)], limit=1)
                if mirror_sku:
                    selected_mirror = request.env['product.product'].sudo().search([('default_code', '=', mirror_sku)], limit=1)
                if faucet_sku:
                    selected_faucet = request.env['product.product'].sudo().search([('default_code', '=', faucet_sku)], limit=1)

                if product:
                    template = product.product_tmpl_id
                    tag_names = template.product_tag_ids.mapped('name')

                    excluded_tags = [
                        'Vanity Only', 'Bathroom Vanities', 'Bathroom Vanities (Cabinet)', 'Vanity, Countertop, Sink, and Mirror', 'Vanity, Countertop, and Sink',
                        'Vanity, Countertop, Sink, and Faucet', 'Vanity, Countertop, Sink, Mirror, and Faucet',
                        'Single', 'Double', 'Sink', 'Countertops', 'Top', 'Acrylic', 'Frameless'
                    ]

                    collection_tag = next((tag for tag in tag_names if not tag.isdigit() and tag not in excluded_tags), None)
                    excluded_for_color = excluded_tags + [collection_tag]
                    color_tag = next((tag for tag in tag_names if not tag.isdigit() and tag not in excluded_for_color), None)

                    tag_model = request.env['product.tag'].sudo()
                    vanity_only_tag = tag_model.search([('name', '=', 'Vanity Only')])
                    bv_tag = tag_model.search([('name', '=', 'Bathroom Vanities')])
                    bv_cabinet_tag = tag_model.search([('name', '=', 'Bathroom Vanities (Cabinet)')])
                    collection_tag_obj = tag_model.search([('name', '=', collection_tag)]) if collection_tag else None
                    color_tag_obj = tag_model.search([('name', '=', color_tag)]) if color_tag else None

                    if vanity_only_tag and (bv_tag or bv_cabinet_tag) and collection_tag_obj and color_tag_obj:
                        candidate_templates = request.env['product.template'].sudo().search([])

                        def matches_required_tags(template):
                            tags = template.product_tag_ids
                            return (
                                vanity_only_tag in tags and
                                (bv_tag in tags or bv_cabinet_tag in tags) and
                                collection_tag_obj in tags and
                                color_tag_obj in tags
                            )

                        size_templates = candidate_templates.filtered(matches_required_tags)
                        related_sizes = request.env['product.product'].sudo().search([
                            ('product_tmpl_id', 'in', size_templates.ids)
                        ])

                    size_tags = template.product_tag_ids.filtered(lambda t: t.name.isdigit())
                    candidate_templates = request.env['product.template'].sudo().search([])

                    # Countertops
                    countertop_tag = tag_model.search([('name', '=', 'Countertops')])
                    if countertop_tag and collection_tag_obj and size_tags:
                        def matches_countertop_tags(template):
                            tags = template.product_tag_ids
                            return (
                                countertop_tag in tags and
                                collection_tag_obj in tags and
                                any(tag in tags for tag in size_tags)
                            )
                        top_templates = candidate_templates.filtered(matches_countertop_tags)
                        related_countertops = request.env['product.product'].sudo().search([
                            ('product_tmpl_id', 'in', top_templates.ids)
                        ])

                    # Mirrors
                    mirror_tag = tag_model.search([('name', '=', 'Mirrors')])
                    if mirror_tag and collection_tag_obj and size_tags:
                        def matches_mirror_tags(template):
                            tags = template.product_tag_ids
                            return (
                                mirror_tag in tags and
                                collection_tag_obj in tags and
                                any(tag in tags for tag in size_tags)
                            )
                        mirror_templates = candidate_templates.filtered(matches_mirror_tags)
                        related_mirrors = request.env['product.product'].sudo().search([
                            ('product_tmpl_id', 'in', mirror_templates.ids)
                        ])

                    # Faucets
                    faucet_tag = tag_model.search([('name', '=', 'Faucet')])
                    if faucet_tag and collection_tag_obj and size_tags:
                        def matches_faucet_tags(template):
                            tags = template.product_tag_ids
                            return (
                                faucet_tag in tags and
                                collection_tag_obj in tags and
                                any(tag in tags for tag in size_tags)
                            )
                        faucet_templates = candidate_templates.filtered(matches_faucet_tags)
                        related_faucets = request.env['product.product'].sudo().search([
                            ('product_tmpl_id', 'in', faucet_templates.ids)
                        ])

                            # After fetching related_sizes, related_countertops, related_mirrors, related_faucets
                    # Fetch related kits for each product by their default_code

                    def get_kit_by_product(product):
                        if not product:
                            return None
                        return request.env['product.kits'].sudo().search([
                            '|',
                            ('cabinet_sku', '=', product.default_code),
                            '|',
                            ('counter_top_sku', '=', product.default_code),
                            '|',
                            ('mirror_sku', '=', product.default_code),
                            ('faucet_sku', '=', product.default_code),
                        ], limit=1)

                    related_size_kits = [get_kit_by_product(prod) for prod in related_sizes]
                    related_countertop_kits = [get_kit_by_product(prod) for prod in related_countertops]
                    related_mirror_kits = [get_kit_by_product(prod) for prod in related_mirrors]
                    related_faucet_kits = [get_kit_by_product(prod) for prod in related_faucets]

        # Pass these lists to template
        return request.render('product_configuration.template_product_configuration', {
            'product': product,
            'related_sizes': related_sizes,
            'related_size_kits': related_size_kits,
            'related_countertops': related_countertops,
            'related_countertop_kits': related_countertop_kits,
            'related_mirrors': related_mirrors,
            'related_mirror_kits': related_mirror_kits,
            'related_faucets': related_faucets,
            'related_faucet_kits': related_faucet_kits,
            'collection_name': collection_tag,
            'color_name': color_tag,
            'selected_countertop_sku': request.params.get('countertop_sku'),
            'selected_mirror_sku': request.params.get('mirror_sku'),
            'selected_faucet_sku': request.params.get('faucet_sku'),
        })
