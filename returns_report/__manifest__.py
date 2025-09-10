{
    'name': 'Returns Report',
    'version': '1.0.0',
    'summary': 'Custom model for Returns Report',
    'description': 'A new model returns.report inheriting stock.move.line structure via delegation.',
    'category': 'Inventory/Inventory',
    'author': 'Karl Areglado',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/returns_report_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
