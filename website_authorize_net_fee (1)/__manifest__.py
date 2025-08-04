{
    'name': 'Website Authorize.Net Fee',
    'version': '1.0',
    'summary': 'Add 3.5% Authorize.Net fee to Sale Order during checkout',
    'description': """
        - Dynamically displays a 3.5% fee when Authorize.Net is selected.
        - Adds fee line to Sale Order before payment.
        - Links payment provider to the Sale Order.
    """,
    'author': 'Your Name or Company',
    'website': 'https://yourcompany.com',
    'category': 'Website',
    'depends': [
        'website_sale',
        'payment',
        'sale_management',
    ],
    'data': [
        'data/fee_product.xml',
        'views/templates.xml',
        'views/payment_provider_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_authorize_net_fee/static/src/js/payment_fee.js',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
