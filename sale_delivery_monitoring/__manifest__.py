{
    'name': 'Sale Delivery Monitoring',
    'version': '1.0.0',
    'summary': 'Add delivery tracking fields & EDD on Sale Orders and daily autobucketing',
    'category': 'Sales',
    'author': 'You',
    'license': 'LGPL-3',
    'depends': ['sale_management'],
    'data': [
        'views/sale_order_views.xml',
        'data/cron.xml',
    ],
    'installable': True,
    'application': False,
}
