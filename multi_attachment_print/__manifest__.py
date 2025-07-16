{
    'name': 'Multi Attachment Print',
    'version': '1.0',
    'summary': 'Print multiple ir.attachment PDFs',
    'category': 'Tools',
    'license': 'LGPL-3',
    'depends': ['web'],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'multi_attachment_print/static/src/js/custom_attachment_download.js',
        ],
    },
    'installable': True,
    'application': False,
}
