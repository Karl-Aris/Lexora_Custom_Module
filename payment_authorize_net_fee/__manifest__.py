{
    'name': 'Authorize.Net Payment Fee',
    'version': '1.0',
    'summary': 'Add 3.5% surcharge for Authorize.Net payments',
    'category': 'Accounting',
    'depends': ['payment', 'sale', 'account', 'website_sale'],
    'data': [],
    'assets': {
        'web.assets_frontend': [
            'payment_authorize_net_fee/static/src/js/authorize_net_fee_notice.js',
        ],
    },
    'installable': True,
    'application': False,
}
