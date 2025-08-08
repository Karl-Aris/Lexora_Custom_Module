{
    'name': 'Authorize.Net Payment Fee',
    'version': '1.0',
    'summary': 'Add 3.5% surcharge for Authorize.Net payments on Sale Orders',
    'category': 'Accounting',
    'author': 'Your Name',
    'depends': ['sale', 'payment'],
    'data': [
        'views/payment_authorize_net_fee_templates.xml',
    ],
    'installable': True,
    'application': False,
}
