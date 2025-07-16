{
    'name': 'Multi Attachment Print',
    'version': '1.0',
    'summary': 'Print multiple ir.attachment PDFs',
    'category': 'Tools',
    'depends': ['base'],
    'data': [
        # Add your XML/CSV data files here if needed
    ],
    'assets': {
        'web.assets_backend': [
            'multi_attachment_print/static/src/js/custom_attachment_download.js',
        ],
    },
    'installable': True,
    'application': False,
}
