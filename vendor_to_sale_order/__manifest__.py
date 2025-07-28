{
    'name': 'Sale Order Vendor Bill Link',
    'version': '1.0',
    'depends': ['sale', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'views/account_move_view.xml',
        'views/vendor_bill_wizard_view.xml',
    ],
    'installable': True,
    'application': False,
}
