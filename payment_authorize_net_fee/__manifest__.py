{
    'name': 'Authorize.Net Payment Fee',
    'version': '1.0',
    'summary': 'Popup notice for Authorize.Net 3.5% fee',
    'category': 'Accounting',
    'depends': ['payment', 'website_sale', 'web'],
    'assets': {
        'web.assets_frontend': [
            'payment_authorize_net_fee/static/src/js/authorize_net_fee_notice.js',
        ],
    },
    'installable': True,
    'application': False,
}
