{
    "name": "Block Inventory Adjustment",
    "version": "1.0",
    "depends": ["stock"],
    "author": "ChatGPT Custom",
    "category": "Inventory",
    "description": "Restricts Inventory Adjustment unless explicitly allowed.",
    "data": [
        "security/inventory_block_rules.xml",
        "security/ir.model.access.csv",
        "views/inventory_menu.xml"
    ],
    "installable": True,
    "application": False,
}
