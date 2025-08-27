from odoo import models, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name and self.env.context.get("search_multi_po"):
            terms = [t.strip() for t in name.replace("\n", ",").split(",") if t.strip()]
            if terms:
                domain = ["|"] * (len(terms) - 1)
                domain += [("purchase_order", "=", t) for t in terms]
                args = args + [domain]
        return super()._name_search(name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)