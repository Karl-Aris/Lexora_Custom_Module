from odoo import api, SUPERUSER_ID

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    provider = env['payment.provider'].search([('code', '=', 'mock_authorize_net')], limit=1)
    if not provider:
        env['payment.provider'].create({
            'name': 'Mock Authorize.Net',
            'code': 'mock_authorize_net',
            'module_id': env.ref('base.module_payment_mock_authorize_net_fee').id,
        })