import logging
from odoo import models

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def search(self, args, offset=0, limit=None, order=None):
        _logger.info(">>> Incoming search args: %s", args)  # Debugging

        new_args = []
        for arg in args:
            if isinstance(arg, (list, tuple)) and arg[0] == 'purchase_order':
                operator = arg[1]
                value = arg[2]

                if operator in ('ilike', '=ilike', '=', '==') and isinstance(value, str):
                    # Normalize separators (comma, newline, space)
                    terms = [t.strip() for t in value.replace('\n', ',').replace(' ', ',').split(',') if t.strip()]
                    if len(terms) > 1:
                        # Build OR domain using strict '=' operator
                        domain = ['|'] * (len(terms) - 1)
                        for term in terms:
                            domain.append(('purchase_order', '=', term))
                        new_args.append(domain)
                        continue
            new_args.append(arg)

        return super(SaleOrder, self).search(new_args, offset=offset, limit=limit, order=order)
