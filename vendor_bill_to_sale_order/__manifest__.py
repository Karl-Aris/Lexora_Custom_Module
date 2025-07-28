{
    'name': 'Sale Order to Vendor Bill Link',
    'version': '1.0',
    'category': 'Accounting',
    'depends': ['sale', 'account'],
    'data': [
        'views/account_move_view.xml',
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
