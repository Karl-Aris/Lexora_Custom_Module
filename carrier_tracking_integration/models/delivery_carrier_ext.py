from odoo import models, fields

class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    # Choose which integration logic this carrier uses
    carrier_vendor = fields.Selection([
        ("ups", "UPS"),
        ("xpo", "XPO Logistics"),
        ("none", "None/Other"),
    ], string="Carrier Vendor", default="none", help="Used by the Track Shipment button.")

    # UPS credentials (REST)
    ups_access_key = fields.Char("UPS Access Key / Client ID")
    ups_client_secret = fields.Char("UPS Client Secret")
    ups_username = fields.Char("UPS Username")
    ups_password = fields.Char("UPS Password")
    ups_account_number = fields.Char("UPS Account Number")
    ups_use_sandbox = fields.Boolean("UPS Sandbox", default=True,
                                     help="Use UPS test environment (wwwcie).")

    # XPO credentials (placeholder; adjust to your contract)
    xpo_api_key = fields.Char("XPO API Key")
    xpo_use_sandbox = fields.Boolean("XPO Sandbox", default=True)
