{
    'name': 'Website Payment Fee UI',
    'version': '17.0.1.0.0',
    'category': 'Website',
    'summary': 'Display dynamic payment method fees in the website checkout UI.',
    'description': """
Adds per-payment-method fee display logic to website checkout.
""",
    'author': 'Your Name or Company',
    'website': 'https://yourwebsite.com',
    'depends': [
        'website_sale',
        'payment',
    ],
    'data': [
        'views/payment_provider_views.xml',
        'views/templates.xml',
    ],
    'assets': {
        'website.assets_frontend': [
            'website_payment_fee_ui/static/src/js/payment_fee.js',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
