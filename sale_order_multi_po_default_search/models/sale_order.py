from odoo import models, api

def _split_terms(text):
    if not text:
        return []
    for sep in ('\n', ',',):
        text = text.replace(sep, ' ')
    parts = [p.strip() for p in text.split(' ') if p and p.strip()]
    seen, terms = set(), []
    for p in parts:
        if p not in seen:
            seen.add(p)
            terms.append(p)
    return terms

def _or_domain_on_po(terms):
    # Return a flat OR domain, not nested
    dom = []
    for idx, t in enumerate(terms):
        if idx > 0:
            dom.insert(0, '|')
        dom.append(('purchase_order', 'ilike', t))
    return dom

def _transform_domain(domain):
    """Replace ('purchase_order','ilike','multi words') with OR conditions flat"""
    if not isinstance(domain, list):
        return domain

    new_domain = []
    for item in domain:
        if isinstance(item, tuple) and len(item) >= 3 and item[0] == 'purchase_order' and item[1] == 'ilike':
            terms = _split_terms(item[2])
            if len(terms) > 1:
                new_domain += _or_domain_on_po(terms)
            else:
                new_domain.append(item)
        elif isinstance(item, list):
            new_domain.append(_transform_domain(item))
        else:
            new_domain.append(item)
    return new_domain


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _search(self, args, offset=0, limit=None, order=None):
        try:
            args = _transform_domain(args)
        except Exception:
            pass
        return super()._search(args, offset=offset, limit=limit, order=order)

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            terms = _split_terms(name)
            if terms:
                args += [_or_domain_on_po(terms)]
        return super()._name_search(name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
