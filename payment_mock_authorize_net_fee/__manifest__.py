{
    "name": "Mock Authorize.Net Payment Fee",
    "version": "1.0",
    "depends": ["payment"],
    "category": "Accounting",
    "installable": True,
    "auto_install": False,
    "data": [
        # "data/payment_provider_data.xml",
    ],
    "post_init_hook": "post_init_hook",  # <<== required!
}
