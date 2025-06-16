{
    'name': 'Google Sheet Embedder',
    'version': '1.0',
    'summary': 'Embed editable Google Sheet iframe',
    'category': 'Tools',
    'depends': ['base', 'web'],
    'data': [
        'views/google_sheet_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'your_module/static/src/js/html_frame_widget.js',
        ],
    },
    'installable': True,
    'application': True,
}
