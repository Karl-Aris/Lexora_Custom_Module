{
    'name': 'Sale Order Delivery Tracking',
    'version': '1.1',
    'category': 'Sales',
    'summary': 'Adds delivery tracking fields and grouped filters',
    'author': 'Carl',
    'depends': ['sale'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sale_order_delivery_tracking/static/src/js/search_favorites_menu.js',
            'sale_order_delivery_tracking/static/src/xml/search_favorites_menu.xml',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
