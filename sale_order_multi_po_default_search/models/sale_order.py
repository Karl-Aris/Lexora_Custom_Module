from odoo import models, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []

        if name:
            # Replace newlines, commas, multiple spaces with a single space
            text = name.replace('\n', ' ').replace(',', ' ')
            terms = [t.strip() for t in text.split(' ') if t.strip()]

            if terms:
                domain = []
                for term in terms:
                    if domain:
                        domain = ['|'] + domain
                    domain.append(('purchase_order', 'ilike', term))
                args = args + [domain]

        return super(SaleOrder, self)._name_search(
            name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid
        )
