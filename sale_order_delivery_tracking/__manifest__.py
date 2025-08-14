{
    'name': 'Sale Order Tracking Status',
    'version': '17.0.1.0.0',
    'summary': 'Track delivery status in sale orders',
    'category': 'Sales',
    'author': 'Custom',
    'website': '',
    'depends': ['sale_management'],
    'data': [
        'views/sale_order_view.xml',
        'data/cron.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
