from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _search(self, args, offset=0, limit=None, order=None, count=False):
        # If there's a plain-text search in the domain, split and inject into purchase_order
        new_args = []
        for arg in args:
            if isinstance(arg, tuple) and arg[0] == '__search':
                value = arg[2]
                if value:
                    phrases = [v.strip() for v in value.replace("\n", ",").split(",") if v.strip()]
                    if phrases:
                        domain = ["|"] * (len(phrases) - 1)
                        domain += [("purchase_order", "ilike", phrase) for phrase in phrases]
                        new_args.append(domain)
                    else:
                        new_args.append(arg)
                else:
                    new_args.append(arg)
            else:
                new_args.append(arg)

        return super()._search(new_args, offset=offset, limit=limit, order=order, count=count)
