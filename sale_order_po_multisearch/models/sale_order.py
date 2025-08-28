# models/sale_order.py
from odoo import models, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Intercept the domain and expand multi-line search terms into OR domain."""
        new_args = []
        for arg in args:
            if isinstance(arg, (list, tuple)) and len(arg) == 3:
                field, operator, value = arg
                if field == "purchase_order" and isinstance(value, str) and "\n" in value:
                    # Split by lines
                    terms = [t.strip() for t in value.splitlines() if t.strip()]
                    if len(terms) > 1:
                        # Build OR domain
                        domain = ["|"] * (len(terms) - 1)
                        for t in terms:
                            domain.append((field, operator, t))
                        new_args.extend(domain)
                        continue
            new_args.append(arg)
        return super().search(new_args, offset=offset, limit=limit, order=order, count=count)
