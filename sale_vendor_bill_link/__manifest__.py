{
    'name': 'Sale Order - Vendor Bill Link',
    'version': '1.0',
    'depends': ['sale', 'account'],
    'author': 'Your Name',
    'category': 'Sales',
    'description': 'Adds a button to create/view vendor bills from sale orders.',
    'data': [
        'views/sale_order_form_inherit_vendorbillbutton.xml',
    ],
    'installable': True,
    'application': False,
}
