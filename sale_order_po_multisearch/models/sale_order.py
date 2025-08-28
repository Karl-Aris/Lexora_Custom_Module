from odoo import models, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            terms = [t.strip() for t in name.splitlines() if t.strip()]
            if terms:
                domain = ["|"] * (len(terms) - 1)
                for t in terms:
                    domain.append(("purchase_order", operator, t))
                return self.search(domain + args, limit=limit).name_get()
        return super().name_search(name=name, args=args, operator=operator, limit=limit)
