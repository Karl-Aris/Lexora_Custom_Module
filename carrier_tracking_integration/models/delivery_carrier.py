from odoo import fields, models

class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    tracking_integration_enabled = fields.Boolean(
        string="Enable Tracking Integration",
        help="Enable API integration with the carrier for tracking"
    )
    tracking_api_key = fields.Char(
        string="Tracking API Key",
        help="API Key for the carrier tracking service"
    )
    tracking_account_number = fields.Char(
        string="Tracking Account Number",
        help="Account number provided by the carrier"
    )
    tracking_carrier = fields.Selection(
        [
            ('ups', 'UPS'),
            ('fedex', 'FedEx'),
            ('dhl', 'DHL'),
            ('usps', 'USPS'),
        ],
        string="Tracking Carrier",
        help="Select which carrier to integrate with"
    )
