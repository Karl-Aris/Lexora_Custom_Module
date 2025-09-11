{
    'name': 'Return Order Integration (Fixed)',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Manage Return Orders linked with Stock Picking (WH/INT/RETURN).',
    'depends': ['sale', 'stock', 'stock_barcode'],
    'data': [
        'security/ir.model.access.csv',
        'views/return_order_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
