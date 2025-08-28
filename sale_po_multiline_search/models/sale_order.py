from odoo import models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _expand_multi_po_terms(self, domain):
        """Expand ilike search on purchase_order (or x_po_so_id) into multiple OR conditions
        if the search value has newlines or commas.
        """
        new_domain = []
        for token in domain:
            if (
                isinstance(token, (list, tuple))
                and len(token) == 3
                and token[0] in ("purchase_order", "x_po_so_id")
                and token[1] in ("ilike", "like")
                and token[2]
                and ("," in token[2] or "\n" in token[2])
            ):
                # Split by commas and newlines
                parts = [p.strip() for p in token[2].replace("\r", "").replace(",", "\n").split("\n") if p.strip()]
                if parts:
                    or_domain = []
                    for part in parts:
                        if or_domain:
                            or_domain.append("|")
                        or_domain.append((token[0], token[1], part))
                    new_domain.extend(or_domain)
                else:
                    new_domain.append(token)
            else:
                new_domain.append(token)
        return new_domain

    def search(self, domain=None, *args, **kwargs):
        expanded = self._expand_multi_po_terms(domain or [])
        return super().search(expanded, *args, **kwargs)

    def search_count(self, domain=None, *args, **kwargs):
        expanded = self._expand_multi_po_terms(domain or [])
        return super().search_count(expanded, *args, **kwargs)
