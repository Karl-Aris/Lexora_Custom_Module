{
    'name': 'Sale Delivery Monitoring',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Track and auto-update delivery status for sale orders',
    'author': 'Custom',
    'depends': ['sale_management'],
    'data': [
        'views/sale_order_views.xml',
        'data/cron_job.xml',
    ],
    'installable': True,
    'application': False,
}
