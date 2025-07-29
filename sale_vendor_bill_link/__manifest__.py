{
    "name": "Sale Vendor Bill Link",
    "version": "1.0",
    "summary": "Link Vendor Bills to Sale Orders",
    "category": "Sales",
    "depends": ["sale_management", "account"],
    "data": [
        "views/sale_vendor_bill_action.xml",
        "views/sale_order_view.xml",
        "views/account_move_view.xml",
    ],
    "application": True,
    "installable": True,
    "license": "OEEL-1",
}
