{
    'name': 'Authorize.Net Payment Fee',
    'version': '1.0',
    'summary': 'Add 3.5% surcharge for Authorize.Net payments with customer notice',
    'category': 'Accounting',
    'depends': ['payment', 'sale', 'account', 'website_sale'],
    'data': [
        'views/sale_order_portal_inherit.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'payment_authorize_net_fee/static/src/js/authorize_net_fee_portal.js',
        ],
    },
    'installable': True,
    'application': False,
}
