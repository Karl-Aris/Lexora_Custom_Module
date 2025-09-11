{ 
    'name': "Return Order Integration",
    'version': "1.0",
    'summary': "Integrate warehouse return pickings and barcode returns with a Return Order model and Sales Order view",
    'description': """Creates a return.order model linked to sale.order and stock.picking.
Auto-creates return.order on return pickings (WH/INT/RETURN) and updates status on validation.
Adds a Returns tab on Sale Order and a Returns menu under Sales.""",
    'author': "Generated for Carl",
    'category': 'Warehouse',
    'depends': ['sale', 'stock', 'stock_barcode'],
    'data': [
        'security/ir.model.access.csv',
        'views/return_order_views.xml',
        'views/return_order_menu.xml',
        'views/sale_order_inherit.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
