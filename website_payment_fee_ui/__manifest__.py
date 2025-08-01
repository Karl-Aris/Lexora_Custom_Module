{
    "name": "Website Payment Fee UI",
    "version": "1.0",
    "depends": ["website_sale", "payment"],
    "author": "Custom",
    "category": "Website",
    "description": "Adds payment provider fees in checkout UI and to Sale Order",
    "data": [
        "views/payment_provider_views.xml",
        "views/templates.xml"
    ],
    "assets": {
        "web.assets_frontend": [
            "/website_payment_fee_ui/static/src/js/payment_fee.js"
        ]
    },
    "installable": True,
    "application": False,
    "auto_install": False
}