from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    purchase_order = fields.Char(string="Purchase Order")

    @api.model
    def _name_search(self, name="", args=None, operator="ilike", limit=100, name_get_uid=None):
        """
        Custom search on purchase_order:
        - Splits pasted input by commas (phrase-based search)
        - Each phrase is matched with ilike
        Example:
            Input: "TEST 13 SO, TEST 11 SO, TEST 10 AGAIN PO"
            Domain: ['|','|',
                     ('purchase_order','ilike','TEST 13 SO'),
                     ('purchase_order','ilike','TEST 11 SO'),
                     ('purchase_order','ilike','TEST 10 AGAIN PO')]
        """
        args = list(args or [])
        if name:
            # split only by comma to preserve phrases
            search_terms = [t.strip() for t in name.split(",") if t.strip()]
            if search_terms:
                domain = ["|"] * (len(search_terms) - 1) + [
                    ("purchase_order", "ilike", term) for term in search_terms
                ]
                return self.search(domain + args, limit=limit).name_get()

        return super()._name_search(name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
