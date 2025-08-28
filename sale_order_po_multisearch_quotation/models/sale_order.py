import logging
from odoo import models

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def search(self, args, offset=0, limit=None, order=None):
        _logger.info(">>> Incoming search args: %s", args)  # Debug line

        new_args = []
        for arg in args:
            if isinstance(arg, (list, tuple)) and arg[0] == 'purchase_order' and isinstance(arg[2], str):
                raw_value = arg[2]
                # try splitting on comma and also space
                terms = [t.strip() for t in raw_value.replace('\n', ',').replace(' ', ',').split(',') if t.strip()]
                if len(terms) > 1:
                    domain = ['|'] * (len(terms) - 1)
                    for term in terms:
                        domain.append(('purchase_order', arg[1], term))
                    new_args.append(domain)
                    continue
            new_args.append(arg)

        return super(SaleOrder, self).search(new_args, offset=offset, limit=limit, order=order)
