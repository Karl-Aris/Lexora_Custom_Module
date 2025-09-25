import re
from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    purchase_order = fields.Char(string="Purchase Order")

    def _tokenize(self, text):
        """Split by whitespace, comma, semicolon or newline into tokens."""
        if not text:
            return []
        return [t for t in re.split(r"[,\s;]+", text.strip()) if t]

    def _make_or_domain(self, field, tokens):
        """Return a flat OR domain like ['|','|',cond1,cond2,cond3] with '=' operator."""
        conds = [(field, "=", t) for t in tokens]
        if len(conds) > 1:
            return ["|"] * (len(conds) - 1) + conds
        return conds

    @api.model
    def search_purchase_order(self, value, limit=100):
        """
        Custom search method for purchase_order field.
        Does not affect global _search.
        """
        tokens = self._tokenize(value)
        if not tokens:
            return self.browse()

        if len(tokens) > 1:
            domain = self._make_or_domain("purchase_order", tokens)
        else:
            domain = [("purchase_order", "=", tokens[0])]

        return self.search(domain, limit=limit)
