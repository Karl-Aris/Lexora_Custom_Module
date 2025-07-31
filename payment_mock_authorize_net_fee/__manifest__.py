{
    "name": "Mock Authorize.Net Payment Fee",
    "version": "1.0",
    "depends": ["payment"],
    "category": "Accounting",
    "installable": True,
    "auto_install": False,
    "post_init_hook": "payment_mock_authorize_net_fee.hooks.post_init_hook",
    "data": [
        "data/payment_provider_data.xml"
    ]
}
