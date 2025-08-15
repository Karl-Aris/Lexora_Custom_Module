from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = "sale.order"

    # If your field already exists from Studio or another module,
    # you may remove the definition below and keep only the group_expand method.
    x_delivery_status = fields.Selection(
        selection=[
            ("pending", "Pending"),
            ("shipped", "Shipped"),
            ("delivered", "Delivered"),
        ],
        string="Delivery Status",
        help="Custom delivery status used for grouping in the search view.",
        group_expand="_group_expand_x_delivery_status",
    )

    def _group_expand_x_delivery_status(self, values, domain, order):
        """
        Ensure the Group By dropdown shows all selection keys
        regardless of whether records exist for each value.
        """
        selection_dict = dict(self._fields['x_delivery_status'].selection)
        # Return the keys in a stable order as defined in selection
        return list(selection_dict.keys())