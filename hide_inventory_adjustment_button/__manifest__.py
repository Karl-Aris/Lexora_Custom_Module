{
    "name": "Hide Inventory Adjustment Button in Barcode",
    "version": "1.0",
    "category": "Stock",
    "summary": "Hides the Inventory Adjustment button in Barcode dashboard",
    "author": "ChatGPT",
    "depends": ["stock_barcode"],
    "data": [
        "views/assets.xml"
    ],
    "assets": {
        "web.assets_backend": [
            "/hide_inventory_adjustment_button/static/src/css/hide_inventory_button.css"
        ]
    },
    "installable": True,
    "application": False,
    "auto_install": False
}
