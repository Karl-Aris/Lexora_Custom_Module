{
    'name': 'Sale Order Delivery Tracking',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Track delivery status, EDD, and follow-up in Sale Orders',
    'description': 'Custom module to track delivery status, EDD, and customer follow-ups.',
    'depends': ['sale'],
    'data': [
        'views/sale_order_delivery_tracking_views.xml',
        'data/sale_order_delivery_tracking_data.xml',
    ],
    'installable': True,
    'application': False,
}
