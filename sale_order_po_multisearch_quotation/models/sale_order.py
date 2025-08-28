import logging
from odoo import models

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def search(self, args, offset=0, limit=None, order=None):
        _logger.info(">>> Incoming search args: %s", args)

        new_args = []
        for arg in args:
            if isinstance(arg, (list, tuple)) and arg[0] == 'purchase_order':
                operator = arg[1]
                value = arg[2]

                if operator in ('ilike', '=ilike', '=', '==') and isinstance(value, str):
                    # split value into terms
                    terms = [t.strip() for t in value.replace('\n', ',').split(',') if t.strip()]
                    if len(terms) > 1:
                        # Build OR domain flat at the same level
                        domain = []
                        for i, term in enumerate(terms):
                            if i > 0:
                                domain.append('|')
                            domain.append(('purchase_order', '=', term))
                        _logger.info(">>> Rewritten domain: %s", domain)
                        new_args.append(domain)
                        continue
            new_args.append(arg)

        return super().search(new_args, offset=offset, limit=limit, order=order)
