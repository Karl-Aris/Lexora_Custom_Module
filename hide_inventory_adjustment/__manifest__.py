{
    "name": "Hide Inventory Adjustment Button",
    "version": "1.0",
    "category": "Stock",
    "summary": "Hides the Inventory Adjustments button from the Barcode dashboard",
    "depends": ["stock_barcode"],
    "assets": {
        "web.assets_frontend": [
            "hide_inventory_adjustment_button/static/src/js/hide_button.js"
        ]
    },
    "data": [
        "views/assets_template.xml"
    ],
    "installable": True,
    "application": False,
}
