{
    'name': "Authorize.Net Payment Surcharge Confirmation",
    'version': '1.0',
    'category': 'Accounting/Payment',
    'summary': 'Adds surcharge confirmation page for Authorize.Net payment method',
    'author': "ChatGPT",
    'depends': ['payment', 'website_sale'],
    'data': [
        'views/payment_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
