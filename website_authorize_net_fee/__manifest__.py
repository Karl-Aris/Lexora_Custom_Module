{
    "name": "Website Authorize.Net Fee",
    "version": "1.0",
    "depends": ["website", "website_sale", "payment_authorize", "sale"],
    "category": "Website",
    "summary": "Adds 3.5% fee on selecting Authorize.Net during checkout",
    "author": "Carl A.",
    "data": [
        "views/templates.xml"
    ],
    "assets": {
        "web.assets_frontend": [
            "website_authorize_net_fee/static/src/js/payment_fee.js"
        ]
    },
    "installable": True
}
