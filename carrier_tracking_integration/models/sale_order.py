import logging
import requests
import uuid
from odoo import models, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_fedex_track(self):
        """Called by the FedEx Track button"""
        self.ensure_one()
        # Call your FedEx REST API wrapper here
        tracking_numbers = self.picking_ids.mapped('carrier_tracking_ref')
        if not tracking_numbers:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'FedEx Tracking',
                    'message': 'No tracking numbers found on this order.',
                    'sticky': False,
                }
            }

        # Call your carrier integration service here
        response_msg = f"Tracking numbers: {', '.join(tracking_numbers)}"
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'FedEx Tracking',
                'message': response_msg,
                'sticky': True,
            }
        }
                    }
                }

            except requests.exceptions.RequestException as e:
                raise UserError(_("FedEx tracking request error: %s") % str(e))
