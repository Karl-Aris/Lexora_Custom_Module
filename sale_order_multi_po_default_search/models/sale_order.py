from odoo import models, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            # split by newline, comma, or space
            separators = ['\n', ',', ' ']
            text = name
            for sep in separators:
                text = text.replace(sep, ' ')
            terms = [t.strip() for t in text.split(' ') if t.strip()]
            if len(terms) > 1:
                # Build OR domain only on purchase_order field
                domain = ["|"] * (len(terms) - 1)
                domain += [("purchase_order", "=", t) for t in terms]
                args = args + [domain]
                return self.search(args, limit=limit).name_get()
        return super()._name_search(name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)