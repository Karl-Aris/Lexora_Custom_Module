from odoo import models, fields

class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    # UPS credentials
    ups_username = fields.Char("UPS Username")
    ups_password = fields.Char("UPS Password")
    ups_access_key = fields.Char("UPS Access Key")

    # XPO credentials
    xpo_client_id = fields.Char("XPO Client ID")
    xpo_secret_key = fields.Char("XPO Secret Key")

    # Future carriers can be added here...
