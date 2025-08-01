{
    "name": "Website Payment Fee",
    "version": "1.0",
    "summary": "Display and apply payment method fees during checkout",
    "author": "Carl Custom Dev",
    "depends": ["website_sale", "payment", "sale_management"],
    "data": [
        "views/payment_provider_views.xml",
        "views/assets.xml"
    ],
    "assets": {
        "web.assets_frontend": [
            "/website_payment_fee/static/src/js/payment_fee.js"
        ]
    },
    "installable": True,
    "application": False,
    "auto_install": False
}