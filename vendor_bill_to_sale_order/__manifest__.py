{
    "name": "Vendor Bill from Sales Order",
    "version": "1.0",
    "depends": ["sale", "account"],
    "author": "Carl Areglado",
    "category": "Custom",
    "data": [
        "views/sale_order_view.xml",
        "views/account_move_view.xml",
        "views/vendor_bill_actions.xml",
    ],
    "installable": True,
    "application": False,
}
