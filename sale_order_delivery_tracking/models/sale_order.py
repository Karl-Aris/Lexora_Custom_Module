import requests
from odoo import models, fields, api
from datetime import date

class SaleOrder(models.Model):
    _inherit = "sale.order"

    x_delivery_status = fields.Selection([
        ('shipped', 'Shipped'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('not_delivered_edd', 'Not Delivered on EDD'),
        ('exception', 'Exception')
    ], string="Delivery Status", default=False)

    tracking_number = fields.Char(string="Tracking Number")
    estimated_delivery_date = fields.Date(string="Estimated Delivery Date")
    follow_up_status = fields.Selection([
        ('pending', 'Pending'),
        ('done', 'Done')
    ], string="Follow-Up Status", default=False)

    def fetch_fedex_tracking(self):
        """Fetch tracking info from FedEx API"""
        api_key = self.env['ir.config_parameter'].sudo().get_param('fedex.api_key')
        api_password = self.env['ir.config_parameter'].sudo().get_param('fedex.api_password')
        account_number = self.env['ir.config_parameter'].sudo().get_param('fedex.account_number')
        meter_number = self.env['ir.config_parameter'].sudo().get_param('fedex.meter_number')

        for order in self:
            if not order.tracking_number:
                continue

            # FedEx REST API endpoint (example)
            url = "https://apis-sandbox.fedex.com/track/v1/trackingnumbers"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._get_fedex_token()}"
            }
            payload = {
                "trackingInfo": [{
                    "trackingNumberInfo": {
                        "trackingNumber": order.tracking_number
                    }
                }],
                "includeDetailedScans": True
            }

            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                status_desc = data['output']['completeTrackResults'][0]['trackResults'][0]['latestStatusDetail']['statusByLocale']

                # Map FedEx status to our status field
                status_map = {
                    'Delivered': 'delivered',
                    'In Transit': 'in_transit',
                    'Exception': 'exception',
                    'At Pickup': 'shipped'
                }
                mapped_status = status_map.get(status_desc, False)
                if mapped_status:
                    order.x_delivery_status = mapped_status

                # Log history in chatter
                order.message_post(body=f"FedEx Update: {status_desc}")

    def _get_fedex_token(self):
        """Get OAuth token from FedEx"""
        url = "https://apis-sandbox.fedex.com/oauth/token"
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.env['ir.config_parameter'].sudo().get_param('fedex.api_key'),
            'client_secret': self.env['ir.config_parameter'].sudo().get_param('fedex.api_password')
        }
        response = requests.post(url, data=payload)
        return response.json().get("access_token")
