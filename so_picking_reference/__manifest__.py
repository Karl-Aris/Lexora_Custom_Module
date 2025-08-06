{
    'name': 'Sales Order Picking Reference',
    'version': '1.0',
    'summary': 'Auto-fill Picking IN/OUT from Purchase Order in Sales Order',
    'depends': ['sale_management', 'stock', 'purchase'],
    'author': 'Carl',
    'category': 'Sales',
    'data': [
    'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
}
