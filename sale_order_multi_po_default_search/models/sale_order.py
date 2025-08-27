from odoo import models, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            separators = ['\n', ',', ' ']
            text = name
            for sep in separators:
                text = text.replace(sep, ' ')
            terms = [t.strip() for t in text.split(' ') if t.strip()]
            if terms:
                domain = []
                for term in terms:
                    if domain:
                        domain = ['|'] + domain
                    domain.append(('purchase_order', 'ilike', term))
                args += [domain]
        return super()._name_search(name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
