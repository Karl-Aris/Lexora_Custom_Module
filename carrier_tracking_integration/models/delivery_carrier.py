from odoo import models, fields

class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    fedex_client_id = fields.Char("FedEx Client ID")
    fedex_client_secret = fields.Char("FedEx Client Secret")
    fedex_use_sandbox = fields.Boolean("Use FedEx Sandbox", default=True)

    # cache token per carrier
    fedex_token_cache = fields.Char("FedEx Token Cache", readonly=True)
    fedex_token_expiry = fields.Float("FedEx Token Expiry Timestamp", readonly=True)
