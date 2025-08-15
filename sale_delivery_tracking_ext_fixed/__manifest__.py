{
    'name': 'Sales Delivery Tracking Extensions',
    'summary': 'Adds delivery tracking fields and dashboard filters to Sales Orders',
    'version': '17.0.1.0.1',
    'category': 'Sales',
    'author': 'ChatGPT',
    'license': 'LGPL-3',
    'depends': ['sale', 'delivery'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_delivery_tracking_views.xml',
    ],
    'installable': True,
    'application': False,
}
