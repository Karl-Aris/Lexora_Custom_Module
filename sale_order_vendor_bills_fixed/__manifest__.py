{
    "name": "Sale Order Vendor Bills",
    "version": "1.0",
    "depends": ["sale", "account"],
    "author": "OpenAI",
    "category": "Sales",
    "description": "Link Vendor Bills (account.move) to Sale Orders via one2many field.",
    "data": ["views/sale_order_view.xml"],
    "installable": True,
    "application": False,
}