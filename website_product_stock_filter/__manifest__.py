{
    "name": "Website Product Stock Filter",
    "summary": "Filter shop products by stock availability",
    "version": "1.0",
    "depends": ["website_sale", "website_sale_stock"],
    "data": [
        "views/templates.xml"
    ],
    "assets": {
        "web.assets_frontend": [
            "website_product_stock_filter/static/src/js/product_filter.js"
        ]
    },
    "installable": True,
    "application": False,
    "auto_install": False
}