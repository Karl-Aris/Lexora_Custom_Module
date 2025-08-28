from odoo import models, api
from odoo.http import request

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _expand_po_domain(self, args):
        """Expand purchase_order domain when multiline search is used"""
        new_args = []
        for arg in args:
            if (
                isinstance(arg, (list, tuple))
                and len(arg) == 3
                and arg[0] == "purchase_order"
                and arg[1] in ("ilike", "like")
                and arg[2]
            ):
                # Split on newlines and commas
                terms = [t.strip() for t in arg[2].replace(",", "\n").splitlines() if t.strip()]
                if len(terms) > 1:
                    or_domain = []
                    for term in terms:
                        if or_domain:
                            or_domain.append("|")
                        or_domain.append(("purchase_order", "ilike", term))
                    new_args.extend(or_domain)
                else:
                    new_args.append(arg)
            else:
                new_args.append(arg)
        return new_args

    @api.model
    def search(self, args, offset=0, limit=None, order=None):
        ctx = self._context or {}
        # Only apply in quotations menu
        if ctx.get("params", {}).get("action") == "sale.action_quotations_with_onboarding":
            args = self._expand_po_domain(args)
        return super().search(args, offset=offset, limit=limit, order=order)

    @api.model
    def search_count(self, args):
        ctx = self._context or {}
        if ctx.get("params", {}).get("action") == "sale.action_quotations_with_onboarding":
            args = self._expand_po_domain(args)
        return super().search_count(args)
