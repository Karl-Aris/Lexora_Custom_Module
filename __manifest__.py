{
    'name': 'Custom Sales Order Search',
    'version': '1.0',
    'category': 'Sales',
    'depends': ['sale'],
    'data': [
        'views/custom_search_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'Lexora_Custom_Module/static/src/js/custom_search.js',
        ],
    },
    'installable': True,
    'application': False,
}
