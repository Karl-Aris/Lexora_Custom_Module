{
    "name": "Vendor Bill Linked to Sale Order",
    "version": "1.0",
    "category": "Accounting",
    "summary": "Allows linking Vendor Bills to Sale Orders",
    "author": "ChatGPT",
    "depends": ["account", "sale", "base"],
    "data": [
        "views/sale_order_view.xml",
        "views/account_move_view.xml",
    ],
    "installable": True,
    "application": False,
}
