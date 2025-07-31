def post_init_hook(cr, registry):
    from odoo.api import Environment
    env = Environment(cr, SUPERUSER_ID, {})

    # Only create if it doesn't exist
    if not env['payment.provider'].search([('code', '=', 'mock_authorize_net')]):
        env['payment.provider'].create({
            'name': 'Mock Authorize.Net',
            'code': 'mock_authorize_net',
            'state': 'enabled',
            'is_published': True,
            'sequence': 30,
        })
