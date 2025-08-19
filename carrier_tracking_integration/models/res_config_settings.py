from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    xpo_api_key = fields.Char("XPO API Key")
    ups_client_id = fields.Char("UPS Client ID")
    ups_client_secret = fields.Char("UPS Client Secret")

    def set_values(self):
        super().set_values()
        self.env["ir.config_parameter"].sudo().set_param("carrier_tracking_integration.xpo_api_key", self.xpo_api_key)
        self.env["ir.config_parameter"].sudo().set_param("carrier_tracking_integration.ups_client_id", self.ups_client_id)
        self.env["ir.config_parameter"].sudo().set_param("carrier_tracking_integration.ups_client_secret", self.ups_client_secret)

    def get_values(self):
        res = super().get_values()
        res.update(
            xpo_api_key=self.env["ir.config_parameter"].sudo().get_param("carrier_tracking_integration.xpo_api_key"),
            ups_client_id=self.env["ir.config_parameter"].sudo().get_param("carrier_tracking_integration.ups_client_id"),
            ups_client_secret=self.env["ir.config_parameter"].sudo().get_param("carrier_tracking_integration.ups_client_secret"),
        )
        return res
