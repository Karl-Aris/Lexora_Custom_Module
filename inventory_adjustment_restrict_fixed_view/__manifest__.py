{
    "name": "Inventory Adjustment Restriction",
    "version": "1.0",
    "depends": ["stock"],
    "author": "Custom",
    "category": "Warehouse",
    "summary": "Restrict inventory adjustments unless in scan mode",
    "data": [
        "security/groups.xml",
        "security/inventory_adjustment_security.xml",
        "views/res_company_views.xml",
    ],
    "installable": True,
    "application": False,
}
