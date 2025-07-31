from odoo import api, SUPERUSER_ID

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    if not env['payment.provider'].search([('code', '=', 'mock_authorize_net')]):
        env['payment.provider'].create({
            'name': 'Mock Authorize.Net',
            'code': 'mock_authorize_net',
            'state': 'enabled',
            'is_published': True,
            'sequence': 30,
        })
