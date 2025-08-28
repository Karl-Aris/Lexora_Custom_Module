from odoo import models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _expand_purchase_order_domain(self, args):
        new_args = []
        for arg in args:
            if (
                isinstance(arg, (list, tuple))
                and len(arg) == 3
                and arg[0] == "purchase_order"
                and arg[1] in ("ilike", "like")
                and arg[2]
            ):
                # Split by newlines or commas
                terms = [t.strip() for t in arg[2].replace(",", "\n").split("\n") if t.strip()]
                if len(terms) > 1:
                    ors = []
                    for t in terms:
                        ors.append(("purchase_order", "ilike", t))
                    # Build OR domain dynamically
                    domain = []
                    for i, cond in enumerate(ors):
                        if i > 0:
                            domain.append("|")
                        domain.append(cond)
                    new_args.append(domain)
                else:
                    new_args.append(arg)
            else:
                new_args.append(arg)
        return new_args

    def search(self, args, offset=0, limit=None, order=None):
        # Only apply inside Quotations action
        if self.env.context.get("params", {}).get("action") == self.env.ref("sale.action_quotations_with_onboarding").id:
            args = self._expand_purchase_order_domain(args)
        return super().search(args, offset=offset, limit=limit, order=order)

    def search_count(self, args):
        if self.env.context.get("params", {}).get("action") == self.env.ref("sale.action_quotations_with_onboarding").id:
            args = self._expand_purchase_order_domain(args)
        return super().search_count(args)
