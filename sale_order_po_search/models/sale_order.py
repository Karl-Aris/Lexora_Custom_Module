from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    purchase_order = fields.Char(string="Purchase Order")

    def _search_purchase_order(self, operator, value):
        """
        Custom search for purchase_order
        - Split input by commas or newlines into phrases
        - Apply OR domain with ilike for each phrase
        """
        if not value:
            return []

        # split input into phrases
        phrases = [v.strip() for v in value.replace("\n", ",").split(",") if v.strip()]
        if not phrases:
            return []

        # Build OR domain dynamically
        domain = ["|"] * (len(phrases) - 1)
        domain += [("purchase_order", "ilike", phrase) for phrase in phrases]
        return domain
