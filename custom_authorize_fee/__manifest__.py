{
    "name": "Custom Authorize.Net Fee",
    "version": "1.0",
    "author": "Your Company",
    "category": "Sales",
    "depends": ["sale_management", "website_sale", "payment"],
    "data": [
        "views/sale_order_views.xml",
        "data/product_data.xml"
    ],
    "assets": {
        "web.assets_frontend": [
            "/custom_authorize_fee/static/src/js/payment_fee.js"
        ]
    },
    "installable": True,
    "auto_install": False
}
