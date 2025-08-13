{
    'name': 'Authorize.Net Payment Fee',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Adds 3.5% surcharge for Authorize.Net payments',
    'description': 'Automatically adds a 3.5% fee when Authorize.Net is selected.',
    'depends': ['sale_management', 'account', 'payment'],
    'data': [
        'data/payment_provider_data.xml',
    ],
    'installable': True,
    'application': False,
}
