from odoo import fields, models, api
from odoo.exceptions import UserError

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

    @api.onchange('tracking_integration_enabled')
    def _onchange_tracking_integration_enabled(self):
        """Clear tracking fields when integration is disabled."""
        if not self.tracking_integration_enabled:
            self.tracking_carrier = False
            self.tracking_api_key = False
            self.tracking_account_number = False

    def action_test_tracking_connection(self):
        """Simulate testing the tracking API connection"""
        for carrier in self:
            if not carrier.tracking_integration_enabled:
                raise UserError("Tracking integration is not enabled for this carrier.")

            if not carrier.tracking_api_key or not carrier.tracking_account_number:
                raise UserError("Please configure API Key and Account Number before testing.")

            # 🚀 TODO: Replace this with actual API call logic
            if carrier.tracking_carrier == "ups":
                message = "UPS tracking connection successful (simulated)."
            elif carrier.tracking_carrier == "fedex":
                message = "FedEx tracking connection successful (simulated)."
            elif carrier.tracking_carrier == "dhl":
                message = "DHL tracking connection successful (simulated)."
            elif carrier.tracking_carrier == "usps":
                message = "USPS tracking connection successful (simulated)."
            else:
                message = "Carrier not supported."

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': "Tracking Test",
                    'message': message,
                    'type': 'success',
                    'sticky': False,
                }
            }
