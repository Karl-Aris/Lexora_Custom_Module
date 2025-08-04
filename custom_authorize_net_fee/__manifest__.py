{
    "name": "Authorize.Net Payment Fee",
    "version": "17.0.1.0.0",
    "depends": [
        "sale_management",
        "website_sale",
        "payment",
    ],
    "data": [
        "data/fee_product.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "custom_authorize_net_fee/static/src/js/fee_dynamic.js",
        ],
    },
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
