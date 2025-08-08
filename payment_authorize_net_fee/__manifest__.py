{
    'name': 'Authorize.Net Fee + Provider (mock) + Portal double-pay guard',
    'version': '1.0.0',
    'summary': 'Add Authorize.Net provider, inject 3.5% fee before payment and avoid double payments in portal',
    'author': 'You',
    'depends': ['website_sale', 'sale', 'payment', 'sale_portal'],
    'data': [
        'views/portal_sale_templates.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
