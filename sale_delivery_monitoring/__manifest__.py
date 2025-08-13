{
    'name': 'Sale Delivery Monitoring',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Track delivery status and EDD in Sales Orders',
    'depends': ['sale_management'],
    'data': [
        'views/sale_order_views.xml',
        'data/cron_data.xml',
    ],
    'installable': True,
    'application': False,
}
