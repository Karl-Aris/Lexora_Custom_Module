{
    'name': 'Sale Order Vendor Bill Link',
    'version': '1.0',
    'depends': ['sale', 'account'],
    'data': [
        'views/sale_order_vendor_bill_button.xml',
        'views/sale_order_view.xml',
        'views/account_move_view.xml',
        'views/vendor_bill_action.xml',
        'views/sale_order_vendor_bill_button.xml',
    ],
    'installable': True,
    'application': False,
}
