# -*- coding: utf-8 -*-
{
    'name': 'Sales Delivery Tracking Extensions',
    'summary': 'Adds delivery tracking fields and dashboard filters to Sales Orders',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'author': 'ChatGPT',
    'website': '',
    'license': 'LGPL-3',
    'depends': ['sale', 'delivery'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_delivery_tracking_views.xml',
    ],
    'installable': True,
    'application': False,
}
