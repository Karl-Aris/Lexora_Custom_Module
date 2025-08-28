from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def search(self, args, offset=0, limit=None, order=None):
        """Intercept domain when searching by purchase_order with multiple values"""
        new_args = []
        for arg in args:
            if isinstance(arg, (list, tuple)) and arg[0] == 'purchase_order' and isinstance(arg[2], str):
                # Split by comma
                terms = [t.strip() for t in arg[2].replace('\n', ',').split(',') if t.strip()]
                if len(terms) > 1:
                    # Build OR domain
                    domain = ['|'] * (len(terms) - 1)
                    for term in terms:
                        domain.append(('purchase_order', arg[1], term))
                    new_args.append(domain)
                else:
                    new_args.append(arg)
            else:
                new_args.append(arg)

        return super(SaleOrder, self).search(new_args, offset=offset, limit=limit, order=order)
