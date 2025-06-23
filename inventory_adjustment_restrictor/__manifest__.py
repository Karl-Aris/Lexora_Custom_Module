{
    "name": "Inventory Adjustment Restrictor",
    "version": "16.0.1.0.0",
    "category": "Inventory",
    "summary": "Restricts inventory adjustments unless user is in the special group.",
    "author": "ChatGPT",
    "depends": ["stock"],
    "data": [
        "security/groups.xml",
        "views/hide_inventory_menu.xml"
    ],
    "installable": True,
    "application": False,
}