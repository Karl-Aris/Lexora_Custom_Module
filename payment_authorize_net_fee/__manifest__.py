{
    'name': 'Authorize.Net Payment Fee',
    'version': '1.0',
    'summary': 'Show 3.5% surcharge notice when clicking Pay with Authorize.Net',
    'category': 'Accounting',
    'depends': ['payment', 'sale', 'account', 'website_sale', 'web'],
    'data': [
        # No XML asset file here — Odoo 17 loads assets from this manifest section
    ],
    'assets': {
        'web.assets_frontend': [
            '/payment_authorize_net_fee/static/src/js/authorize_net_fee_notice.js',
        ],
    },
    'installable': True,
    'application': False,
}
