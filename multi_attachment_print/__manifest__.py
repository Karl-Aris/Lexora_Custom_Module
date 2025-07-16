{
    'name': 'Multi Attachment Print',
    'version': '1.0',
    'summary': 'Download multiple ir.attachment PDFs in one go',
    'category': 'Tools',
    'license': 'LGPL-3',
    'depends': ['base', 'web'],
    'data': ['assets.xml'],
    'assets': {
        'web.assets_backend': [
            'multi_attachment_print/static/src/js/multi_attachment_download.js',
        ],
    },
    'installable': True,
    'application': False,
}
