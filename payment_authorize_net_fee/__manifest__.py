{
    'name': 'Authorize.Net Fee Pre-Payment',
    'version': '17.0.1.0.0',
    'summary': 'Add 3.5% surcharge before Authorize.Net payment',
    'category': 'Accounting/Payment',
    'depends': ['sale', 'website_sale', 'payment'],
    'data': [
        'views/assets.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'payment_authorize_net_fee_pre/static/src/js/authorize_net_fee.js',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
}
