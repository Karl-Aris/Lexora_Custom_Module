{
    'name': 'Delivery Tracking Workflow',
    'summary': 'Track shipments with EDD, auto-categorize delivery status, and manage customer follow-ups.',
    'version': '17.0.1.0.0',
    'category': 'Sales/Delivery',
    'author': 'Your Company',
    'license': 'LGPL-3',
    'depends': ['sale_management'],
    'data': [
        'views/sale_order_views.xml',
        'data/ir_cron.xml',
    ],
    'installable': True,
    'application': False,
}
