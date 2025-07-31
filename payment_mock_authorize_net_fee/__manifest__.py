{
    'name': 'Mock Authorize.Net Fee',
    'version': '1.0',
    'category': 'Accounting/Payment',
    'summary': 'Simulate Authorize.Net and apply 3.5% fee on Sales Orders',
    'depends': ['payment', 'sale'],
    'data': [
        'data/payment_provider_data.xml',
    ],
    'installable': True,
    'application': False,
}
