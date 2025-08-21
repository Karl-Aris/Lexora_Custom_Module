{
    'name': 'Carrier Tracking Webhook',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Handle carrier tracking webhooks and store tracking numbers in Sales Orders',
    'depends': ['sale_management'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
}
