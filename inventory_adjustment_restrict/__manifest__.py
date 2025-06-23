{
    "name": "Inventory Adjustment Restriction",
    "version": "1.0",
    "depends": ["stock"],
    "author": "Karl Areglado",
    "category": "Warehouse",
    "description": "Restricts Inventory Adjustments unless during scan period or with access group.",
    "data": [
        "security/inventory_adjustment_security.xml",
        "views/res_company_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
