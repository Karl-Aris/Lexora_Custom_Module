from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    purchase_order = fields.Char(string="Purchase Order")

    @api.model
    def _name_search(self, name="", args=None, operator="ilike", limit=100, name_get_uid=None):
        """
        Custom search on purchase_order:
        - Splits pasted input by commas into phrases
        - Builds an OR domain with ilike for each phrase
        Example:
            Input: "TEST 13 SO, TEST 11 SO, TEST 10 AGAIN PO"
            Domain: ['|','|',
                     ('purchase_order','ilike','TEST 13 SO'),
                     ('purchase_order','ilike','TEST 11 SO'),
                     ('purchase_order','ilike','TEST 10 AGAIN PO')]
        """
        args = list(args or [])
        if name:
            # split by commas to keep full phrases
            phrases = [phrase.strip() for phrase in name.split(",") if phrase.strip()]
            if phrases:
                domain = ["|"] * (len(phrases) - 1) + [
                    ("purchase_order", "ilike", phrase) for phrase in phrases
                ]
                return self.search(domain + args, limit=limit).name_get()

        return super()._name_search(name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
