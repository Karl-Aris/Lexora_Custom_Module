{
    'name': 'Sale Order Vendor Bill Link',
    'version': '1.0',
    'depends': ['sale', 'account'],
    'data': [
        'views/vendor_bill_action.xml', 
        'views/sale_order_vendor_bill_button.xml',
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'application': False,
}
