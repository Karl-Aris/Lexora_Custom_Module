from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    purchase_order = fields.Char(string="Purchase Order")

    @api.model
    def _name_search(self, name="", args=None, operator="ilike", limit=100, name_get_uid=None):
        """
        Custom search on purchase_order:
        - Splits pasted input (by space or comma)
        - Builds an OR domain with ilike for each term
        Example:
            Input: "Test123 test1233, test1"
            Domain: ['|','|',
                     ('purchase_order','ilike','Test123'),
                     ('purchase_order','ilike','test1233'),
                     ('purchase_order','ilike','test1')]
        """
        args = list(args or [])
        if name:
            # allow space or comma separated values
            search_terms = [t.strip() for t in name.replace(",", " ").split() if t.strip()]
            if search_terms:
                domain = ["|"] * (len(search_terms) - 1) + [
                    ("purchase_order", "ilike", term) for term in search_terms
                ]
                return self.search(domain + args, limit=limit).name_get()

        return super()._name_search(name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
