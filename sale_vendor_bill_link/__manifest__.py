{
    'name': 'Sale Order Vendor Bill Link',
    'version': '1.0',
    'summary': 'Manually link a vendor bill to a sale order',
    'author': 'ChatGPT',
    'depends': ['sale_management', 'account'],
    'data': [
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
