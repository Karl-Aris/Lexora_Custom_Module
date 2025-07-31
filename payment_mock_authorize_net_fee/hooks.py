from odoo import api, SUPERUSER_ID

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    provider = env['payment.provider'].search([('code', '=', 'mock_authorize_net')], limit=1)
    if not provider:
        module = env['ir.module.module'].search([('name', '=', 'payment_mock_authorize_net_fee')], limit=1)
        env['payment.provider'].create({
            'name': 'Mock Authorize.Net',
            'code': 'mock_authorize_net',
            'state': 'enabled',
            'support_tokenization': False,
            'module_id': module.id if module else False,
        })
