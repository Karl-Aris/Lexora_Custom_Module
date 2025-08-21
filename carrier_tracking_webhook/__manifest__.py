# -*- coding: utf-8 -*-
{
    'name': 'Carrier Tracking Webhook',
    'version': '1.0',
    'summary': 'Generic webhook handler for carrier tracking updates',
    'description': 'Receive tracking updates from multiple carriers via webhooks and update Sales Orders.',
    'author': 'Karl Areglado',
    'depends': ['sale_management'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'application': False,
    'installable': True,
    'license': 'LGPL-3',
}
