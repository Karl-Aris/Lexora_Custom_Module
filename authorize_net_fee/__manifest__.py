{
    "name": "Authorize.Net Fee",
    "version": "1.0",
    "category": "Website",
    "summary": "Adds a 3.5% surcharge when paying with Authorize.Net",
    "depends": ["website_sale", "payment", "sale"],
    "data": [
        "views/payment_authorize_net_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "authorize_net_fee/static/src/js/authorize_net_fee.js",
            "authorize_net_fee/static/src/scss/authorize_net_fee.scss",
        ],
    },
    "installable": True,
    "auto_install": False,
}
