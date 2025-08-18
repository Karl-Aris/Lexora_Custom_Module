{
    'name': 'Sale Order Favorites Grouping',
    'version': '17.0.1.0.0',
    'summary': 'Group favorite filters in Sale Order list view by predefined groups',
    'category': 'Sales',
    'author': 'Custom Dev',
    'depends': ['web', 'sale_management'],
    'data': [
        'views/assets.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sale_order_favorites_grouping/static/src/js/favorite_menu_dialog.js',
            'sale_order_favorites_grouping/static/src/xml/favorite_menu_dialog.xml',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}