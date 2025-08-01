{
    "name": "Authorize.Net Payment Fee",
    "version": "1.0",
    "category": "Accounting/Payment Acquirers",
    "summary": "Adds 3.5% surcharge when Authorize.Net is selected on website checkout",
    "depends": ["payment", "website_sale"],
    "data": [
        "data/payment_provider_data.xml",
        "views/payment_authorize_net_templates.xml",
        "views/product_product_views.xml"
    ],
    "assets": {
        "web.assets_frontend": [
            "payment_authorize_net_fee/static/src/js/payment_fee_display.js"
        ]
    },
    "installable": True,
    "application": False,
    "license": "LGPL-3"
}
