import re
from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    purchase_order = fields.Char(string="Purchase Order")

    def _tokenize(self, text):
        """Split by whitespace, comma, semicolon or newline into tokens."""
        if not text:
            return []
        return [t for t in re.split(r"[,\s;]+", text.strip()) if t]

    def _make_or_domain(self, field, tokens, operator="="):
        """Return a flat OR domain like ['|','|', cond1, cond2, cond3]."""
        conds = [(field, operator, t) for t in tokens]
        if len(conds) > 1:
            return ["|"] * (len(conds) - 1) + conds
        return conds

    def _make_r_domain(self, field):
        """Return domain for purchase_orders containing '-R'."""
        return [(field, "ilike", "-R")]

    def _search(
        self, domain, offset=0, limit=None, order=None, access_rights_uid=None
    ):
        """Intercept purchase_order searches and expand into OR tokens."""
        new_domain = []
        for arg in domain:
            if isinstance(arg, (list, tuple)) and len(arg) == 3:
                field, operator, value = arg
                if field == "purchase_order" and operator in ("ilike", "like", "=") and value:
                    # Special case: if user typed "-R", expand to search all containing -R
                    if value.strip() == "-R":
                        new_domain.extend(self._make_r_domain(field))
                        continue

                    tokens = self._tokenize(value)
                    if len(tokens) > 1:
                        new_domain.extend(self._make_or_domain(field, tokens))
                        continue
                    else:
                        # single token → force '='
                        arg = (field, "=", tokens[0])
            new_domain.append(arg)

        return super()._search(
            new_domain,
            offset=offset,
            limit=limit,
            order=order,
            access_rights_uid=access_rights_uid,
        )
