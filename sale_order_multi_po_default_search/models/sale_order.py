# -*- coding: utf-8 -*-
from odoo import models, api

def _split_terms(text: str):
    if not text:
        return []
    # Normalize separators: newline, commas, multiple spaces
    for sep in ('\n', ',',):
        text = text.replace(sep, ' ')
    # Collapse duplicates and strip
    parts = [p.strip() for p in text.split(' ') if p and p.strip()]
    # Deduplicate while keeping order
    seen = set()
    terms = []
    for p in parts:
        if p not in seen:
            seen.add(p)
            terms.append(p)
    return terms

def _or_domain_on_po(terms):
    """
    Build an OR domain over ('purchase_order','ilike', term) for each term.
    For n terms, returns a flat list like:
      ['|','|', ('purchase_order','ilike',t1), ('purchase_order','ilike',t2), ('purchase_order','ilike',t3)]
    """
    if not terms:
        return []
    dom = []
    # For k conditions you need (k-1) '|' in front (flat form)
    for idx, t in enumerate(terms):
        if idx > 0:
            dom = ['|'] + dom
        dom.append(('purchase_order', 'ilike', t))
    return dom

def _transform_domain_recursive(node):
    """
    Recursively walk a domain and replace any ('purchase_order','ilike', <multi-words>)
    with an OR domain over the split terms.

    Handles nested lists with &, |, ! operators.
    """
    # If node is a tuple (leaf)
    if isinstance(node, tuple):
        if (
            len(node) >= 3
            and node[0] == 'purchase_order'
            and node[1] == 'ilike'
            and isinstance(node[2], str)
            and any(sep in node[2] for sep in (' ', ',', '\n'))
        ):
            terms = _split_terms(node[2])
            if len(terms) > 1:
                return _or_domain_on_po(terms)
        return node

    # If node is a list (could be a domain or sub-domain)
    if isinstance(node, list):
        out = []
        for item in node:
            transformed = _transform_domain_recursive(item)
            # If a leaf expanded into a list (OR domain), splice it in
            if isinstance(transformed, list):
                out.extend(transformed)
            else:
                out.append(transformed)
        return out

    # Anything else: return unchanged
    return node


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # 1) Transform domains coming from search filters (e.g., "Search PO# for: ...")
    def _search(self, args, offset=0, limit=None, order=None, count=False):
        try:
            new_args = _transform_domain_recursive(args)
        except Exception:
            # Fail-safe: never block searches due to our transformation
            new_args = args
        return super()._search(new_args, offset=offset, limit=limit, order=order, count=count)

    # 2) Make the global quick search behave the same way (split terms on PO#)
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            terms = _split_terms(name)
            if terms:
                # Add our PO# OR domain so quick search can find by split terms.
                args = list(args) + [_or_domain_on_po(terms)]
        return super()._name_search(name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
