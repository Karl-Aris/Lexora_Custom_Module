{
    'name': 'Return Order Auto-Create',
    'version': '1.0',
    'category': 'Warehouse/Sales',
    'summary': 'Auto-create return.order from stock.picking (WH/INT/RETURN in name) and integrate with Sale Order menu',
    'description': 'Creates return.order records when stock pickings with WH/INT/RETURN are created; safe with Studio custom fields.',
    'author': 'Generated for Carl',
    'depends': ['sale', 'stock', 'stock_barcode'],
    'data': [
        'security/ir.model.access.csv',
        'views/return_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
