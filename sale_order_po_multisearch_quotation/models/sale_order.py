from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.context.get("from_sale_order_tree", False):
            new_args = []
            for arg in args:
                if isinstance(arg, (list, tuple)) and len(arg) >= 3 and arg[0] == "purchase_order" and arg[1] == "ilike":
                    raw_value = arg[2]
                    if raw_value and ("\n" in raw_value or "," in raw_value):
                        # Split by newline or comma
                        values = [v.strip() for v in raw_value.replace(",", "\n").split("\n") if v.strip()]
                        if values:
                            # Build OR domain
                            domain = []
                            for val in values:
                                if domain:
                                    domain.append("|")
                                domain.append(("purchase_order", "ilike", val))
                            new_args.append(domain)
                            _logger.debug("Expanded PO search: %s -> %s", raw_value, domain)
                            continue
                new_args.append(arg)
            args = new_args

        # 👇 Call parent with positional arguments (fix!)
        return super().search(args, offset, limit, order, count)
