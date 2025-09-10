{
    'name': 'Returns Report',
    'version': '1.0.0',
    'summary': 'Module for Returns Report',
    'description': 'Adds example fields and business logic to stock.move.line for Odoo 17 Enterprise.',
    'category': 'Inventory/Inventory',
    'author': 'You',
    'depends': ['stock'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/stock_move_line_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}