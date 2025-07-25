{
    'name': 'Sale Order Vendor Bill Tab',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Adds a Vendor Bill tab to Sale Orders',
    'depends': ['sale', 'account'],
    'data': [
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}