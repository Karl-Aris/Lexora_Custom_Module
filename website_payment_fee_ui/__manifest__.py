{
    "name": "Website Payment Fee UI",
    "version": "1.0",
    "depends": ["website_sale", "website", "payment"],
    "author": "Carl Custom Dev",
    "category": "Website",
    "description": "Adds dynamic payment method fees during checkout.",
    "data": [
        "views/payment_provider_views.xml",
        "views/templates.xml"
    ],
    "assets": {
        "website.assets_frontend": [
            "website_payment_fee_ui/static/src/js/payment_fee.js",
        ]
    },
    "installable": True,
    "auto_install": False,
}
