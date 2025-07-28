{
    'name': 'Sale Order Vendor Bill Link',
    'version': '1.0',
    'depends': ['sale', 'account'],
    'data': [
        'views/action.xml',
        'views/sale_order_view.xml',
        'views/account_move_view.xml',
        'views/vendor_bill_action.xml',
    ],
    'installable': True,
    'application': False,
}
