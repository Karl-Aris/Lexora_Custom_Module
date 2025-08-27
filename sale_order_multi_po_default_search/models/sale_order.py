from odoo import models, api


def _split_terms(text):
    if not text:
        return []
    for sep in ('\n', ',', ' '):
        text = text.replace(sep, ' ')
    parts = [p.strip() for p in text.split(' ') if p.strip()]
    seen, terms = set(), []
    for p in parts:
        if p not in seen:
            seen.add(p)
            terms.append(p)
    return terms


def _build_or_domain(field, terms):
    """Return OR domain for multiple terms on given field"""
    if not terms:
        return []
    domain = []
    for idx, t in enumerate(terms):
        if idx > 0:
            domain.insert(0, '|')
        domain.append((field, 'ilike', t))
    return domain


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # This catches autocomplete (Search PO# selected)
    @api.model
    def _search_panel_domain(self, field_name, values, comodel_domain=None):
        domain = super()._search_panel_domain(field_name, values, comodel_domain=comodel_domain)
        if field_name == 'purchase_order' and values:
            terms = _split_terms(values[0])
            return _build_or_domain('purchase_order', terms)
        return domain

    # This handles quick search (when user just types text)
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []

        if name:
            # Normalize all separators (newline, comma, tab, space)
            for sep in ['\n', '\r', ',', '\t']:
                name = name.replace(sep, ' ')
            terms = [t.strip() for t in name.split(' ') if t.strip()]

            if len(terms) > 1:
                # Build OR domain on purchase_order
                domain = []
                for idx, t in enumerate(terms):
                    if idx > 0:
                        domain.insert(0, '|')
                    domain.append(('purchase_order', 'ilike', t))
                args.append(domain)
                return self.search(args, limit=limit).name_get()

        return super().name_search(name, args=args, operator=operator, limit=limit)
