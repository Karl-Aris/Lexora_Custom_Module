{
    'name': 'Authorize.Net Fee Handler',
    'version': '1.0',
    'depends': ['account', 'payment_authorize'],
    'author': 'Carl Areglado',
    'category': 'Accounting',
    'description': 'Automatically adds a 3% surcharge on invoice if Authorize.Net is used for payment.',
    'data': [
    'data/product_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
