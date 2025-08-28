from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _name_search(self, name='', args=None, operator='ilike', limit=None, name_get_uid=None):
        args = args or []
        if name and self.env.context.get('purchase_order_multisearch'):
            # Split input by comma or newline
            terms = [term.strip() for term in name.replace('\n', ',').split(',') if term.strip()]
            if terms:
                domain = ['|'] * (len(terms) - 1)
                for term in terms:
                    domain.append(('purchase_order', operator, term))
                return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)
        return super()._name_search(name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
