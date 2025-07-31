{
    "name": "Mock Authorize.Net Payment Fee",
    "version": "1.0",
    "category": "Website",
    "summary": "Add 3.5% fee for Mock Authorize.Net payment on Sales Orders",
    "depends": ["payment", "website_sale"],
    "data": [
        "data/payment_acquirer_data.xml",
    ],
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
    "post_init_hook": "post_init_hook"
}