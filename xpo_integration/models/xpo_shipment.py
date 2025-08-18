from odoo import models, fields
import requests

class XPOShipment(models.Model):
    _inherit = "stock.picking"

    xpo_tracking_number = fields.Char(string="XPO Tracking Number")
    xpo_status = fields.Char(string="XPO Status")
    xpo_estimated_delivery = fields.Datetime(string="XPO Estimated Delivery")

    def track_xpo_shipment(self):
        """Fetch tracking info from XPO API (or mock data if API not available)"""
        api_key = self.env['ir.config_parameter'].sudo().get_param('xpo.api_key')
        
        if not self.xpo_tracking_number or not api_key:
            raise ValueError("Tracking number or API key is missing.")

        # MOCK RESPONSE for testing
        data = {
            "status": "In Transit",
            "estimated_delivery": "2025-08-20 18:00:00"
        }

        # Uncomment below for real API once you have credentials
        """
        url = f"https://api.ltl-xpo.com/track/{self.xpo_tracking_number}"
        headers = {"Authorization": f"Bearer {api_key}"}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
            else:
                self.xpo_status = f"Error: {response.status_code}"
                return
        except Exception as e:
            self.xpo_status = f"Request failed: {str(e)}"
            return
        """

        self.xpo_status = data.get("status")
        self.xpo_estimated_delivery = data.get("estimated_delivery")
