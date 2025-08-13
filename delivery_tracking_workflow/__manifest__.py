{
    'name': 'Delivery Tracking Workflow',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Manage shipment tracking and follow-up workflow',
    'description': 'Automates tracking, categorization, and customer follow-up for shipments.',
    'author': 'Your Name',
    'depends': ['sale', 'base'],
    'data': [
        'views/sale_order_views.xml',
        'data/delivery_tracking_data.xml',
    ],
    'installable': True,
    'application': False,
}
