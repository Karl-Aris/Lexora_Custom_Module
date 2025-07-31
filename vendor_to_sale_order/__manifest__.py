{
    'name': 'Sale Order Vendor Bill Link',
    'version': '1.1',
    'depends': ['sale', 'account'],
    'data': [
        'views/account_move_view.xml',
        'views/sale_order_view.xml',
        'views/sale_order_vendor_bill_button.xml',
        'views/vendor_bill_action.xml',
        'views/account_move_mini_form.xml',
    ],
    'installable': True,
    'application': False,
}
