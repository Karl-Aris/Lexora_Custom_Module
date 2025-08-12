{
    'name': 'Sale Order Delivery Lead Time',
    'version': '1.0',
    'summary': 'Compute lead time from order date and delivery date on Sale Orders',
    'category': 'Sales',
    'author': 'Karl Areglado',
    'depends': ['sale'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
