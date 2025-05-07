from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Optional: custom computed or helper fields can be added here
    # For this basic case, we don't need new fields, just the custom search logic
    # But you could add one if needed in the future
