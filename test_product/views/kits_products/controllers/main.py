from odoo import http
from odoo.http import request
from collections import defaultdict

class ProductKitsController(http.Controller):

    def _get_kits(self, name=None, color=None):
        """Helper to get kits by name and optional color."""
        domain = [('name', '=', name)]
        if color:
            domain.append(('color', '=', color))
        else:
            domain.append(('color', '=', False))
        return request.env['product.kits'].sudo().search(domain)

    @http.route(['/product_kits'], type='http', auth="public", website=True)
    def list_kits(self, **kwargs):
        """List all kits grouped by name and color."""
        kits = request.env['product.kits'].sudo().search([])

        grouped_kits = defaultdict(list)
        for kit in kits:
            key = (kit.name, kit.color)
            grouped_kits[key].append(kit)

        return request.render('kits_products.kits_list_template', {
            'grouped_kits': dict(grouped_kits),
        })
    @http.route(['/product_kits/group'], type='http', auth="public", website=True)
    def group_detail(self, name=None, color=None, cabinet=None, counter_top=None, mirror=None, faucet=None, **kwargs):
        """Display kits of a specific group (name + color) and list components for filtering."""
        kits = self._get_kits(name, color)

    # Group components by category
        components = {
        'cabinet': set(),
        'counter_top': set(),
        'mirror': set(),
        'faucet': set(),
        }

        for kit in kits:
            components['cabinet'].update(kit.cabinet_ids)
            components['counter_top'].update(kit.counter_top_ids)
            components['mirror'].update(kit.mirror_ids)
            components['faucet'].update(kit.faucet_ids)

    # Preselect default kit if no selection provided
        default_kit = kits[0] if kits else None

        selected_cabinet = int(cabinet) if cabinet else (default_kit.cabinet_ids[0].id if default_kit and default_kit.cabinet_ids else None)
        selected_counter_top = int(counter_top) if counter_top else (default_kit.counter_top_ids[0].id if default_kit and default_kit.counter_top_ids else None)
        selected_mirror = int(mirror) if mirror else (default_kit.mirror_ids[0].id if default_kit and default_kit.mirror_ids else None)
        selected_faucet = int(faucet) if faucet else (default_kit.faucet_ids[0].id if default_kit and default_kit.faucet_ids else None)

    # Filter kits based on selected components
        filtered_kits = []
        for kit in kits:
            if selected_cabinet and selected_cabinet not in kit.cabinet_ids.ids:
                continue
            if selected_counter_top and selected_counter_top not in kit.counter_top_ids.ids:
                continue
            if selected_mirror and selected_mirror not in kit.mirror_ids.ids:
                continue
            if selected_faucet and selected_faucet not in kit.faucet_ids.ids:
                continue
            filtered_kits.append(kit)

        return request.render('kits_products.kit_group_detail_template', {
        'kits': filtered_kits,
        'name': name,
        'color': color,
        'components': components,
        'cabinet': selected_cabinet,
        'counter_top': selected_counter_top,
        'mirror': selected_mirror,
        'faucet': selected_faucet,
        })

        
                

    @http.route(['/product_kits/group_builder'], type='http', auth="public", website=True)
    def kit_builder(self, name=None, color=None, cabinet=None, counter_top=None, mirror=None, faucet=None, **kwargs):
        kits = self._get_kits(name, color)

        # Group components by category
        components = {
            'cabinet': set(),
            'counter_top': set(),
            'mirror': set(),
            'faucet': set(),
        }

        for kit in kits:
            components['cabinet'].update(kit.cabinet_ids)
            components['counter_top'].update(kit.counter_top_ids)
            components['mirror'].update(kit.mirror_ids)
            components['faucet'].update(kit.faucet_ids)

        # Filter kits based on selected components
        filtered_kits = []
        for kit in kits:
            if cabinet and int(cabinet) not in kit.cabinet_ids.ids:
                continue
            if counter_top and int(counter_top) not in kit.counter_top_ids.ids:
                continue
            if mirror and int(mirror) not in kit.mirror_ids.ids:
                continue
            if faucet and int(faucet) not in kit.faucet_ids.ids:
                continue
            filtered_kits.append(kit)

        return request.render('kits_products.kit_builder_template', {
            'kits': kits,
            'name': name,
            'color': color,
            'components': components,
            'cabinet': int(cabinet) if cabinet else None,
            'counter_top': int(counter_top) if counter_top else None,
            'mirror': int(mirror) if mirror else None,
            'faucet': int(faucet) if faucet else None,
            'filtered_kits': filtered_kits,
        })

    @http.route(['/product_kits/filter'], type='http', auth="public", website=True)
    def filter_kits(self, name=None, color=None, cabinet=None, counter_top=None, mirror=None, faucet=None, **kwargs):
        """Filter kits by selected components."""
        kits = self._get_kits(name, color)

        # Convert component ids to integers for comparison
        filters = {
            'cabinet': int(cabinet) if cabinet else None,
            'counter_top': int(counter_top) if counter_top else None,
            'mirror': int(mirror) if mirror else None,
            'faucet': int(faucet) if faucet else None,
        }

        filtered_kits = []

        for kit in kits:
            if filters['cabinet'] and filters['cabinet'] not in kit.cabinet_ids.ids:
                continue
            if filters['counter_top'] and filters['counter_top'] not in kit.counter_top_ids.ids:
                continue
            if filters['mirror'] and filters['mirror'] not in kit.mirror_ids.ids:
                continue
            if filters['faucet'] and filters['faucet'] not in kit.faucet_ids.ids:
                continue
            filtered_kits.append(kit)

        return request.render('kits_products.filtered_kits_template', {
            'kits': filtered_kits,
            'name': name,
            'color': color,
            **filters,  # Pass component selections back to the template
        })
    http.route(['/product_kits/components'], type='http', auth="public", website=True)
    def kit_components(self, **kwargs):
        """List all kit components grouped by category."""

        kits = request.env['product.kits'].sudo().search([])

        components = {
            'cabinet': set(),
            'counter_top': set(),
            'mirror': set(),
            'faucet': set(),
        }

        for kit in kits:
            components['cabinet'].update(kit.cabinet_ids)
            components['counter_top'].update(kit.counter_top_ids)
            components['mirror'].update(kit.mirror_ids)
            components['faucet'].update(kit.faucet_ids)

        return request.render('kits_products.kit_components_template', {
            'components': components,
        })

    @http.route(['/product_kits/component_filter'], type='http', auth="public", website=True)
    def component_filter(self, category=None, comp_id=None, **kwargs):
        """Filter kits based on a single component selection."""

        kits = request.env['product.kits'].sudo().search([])

        matched_kits = []
        comp_id = int(comp_id)

        for kit in kits:
            if category == 'cabinet' and comp_id in kit.cabinet_ids.ids:
                matched_kits.append(kit)
            elif category == 'counter_top' and comp_id in kit.counter_top_ids.ids:
                matched_kits.append(kit)
            elif category == 'mirror' and comp_id in kit.mirror_ids.ids:
                matched_kits.append(kit)
            elif category == 'faucet' and comp_id in kit.faucet_ids.ids:
                matched_kits.append(kit)

        return request.render('kits_products.filtered_kits_template', {
            'kits': matched_kits,
            'category': category,
            'comp_id': comp_id,
        })