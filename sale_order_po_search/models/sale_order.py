from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    purchase_order = fields.Char(string="Purchase Order")

    def _search_purchase_order(self, operator, value):
        """
        Custom search for Char field purchase_order
        - Split input by commas or newlines into phrases
        - Each phrase searched with ilike (OR logic)
        Example:
            Input: "TEST 13 SO, TEST 11 SO, TEST 10 AGAIN PO"
            Domain: ['|','|',
                     ('purchase_order','ilike','TEST 13 SO'),
                     ('purchase_order','ilike','TEST 11 SO'),
                     ('purchase_order','ilike','TEST 10 AGAIN PO')]
        """
        if not value:
            return []

        # Normalize separators → commas
        phrases = [v.strip() for v in value.replace("\n", ",").split(",") if v.strip()]
        if not phrases:
            return []

        # Build OR domain
        domain = ["|"] * (len(phrases) - 1)
        domain += [("purchase_order", "ilike", phrase) for phrase in phrases]
        return domain
