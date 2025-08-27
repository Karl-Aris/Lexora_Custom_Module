import logging
from odoo import models, api

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []

        if name:
            # Normalize all separators (newline, carriage return, comma, tab)
            for sep in ['\n', '\r', ',', '\t']:
                name = name.replace(sep, ' ')
            terms = [t.strip() for t in name.split(' ') if t.strip()]

            if len(terms) > 1:
                # Build OR domain on purchase_order
                domain = []
                for idx, t in enumerate(terms):
                    if idx > 0:
                        domain.insert(0, '|')
                    domain.append(('purchase_order', 'ilike', t))

                full_domain = args + [domain]
                _logger.info("Multi-line search on sale.order with domain: %s", full_domain)

                return self.search(full_domain, limit=limit).name_get()

        return super().name_search(name, args=args, operator=operator, limit=limit)
