{
    "name": "Carrier Shipment Integration",
    "version": "1.0",
    "category": "Warehouse",
    "summary": "Integrate carrier shipment tracking (XPO, UPS, etc.) into Odoo",
    "description": "Track shipments from multiple carriers (XPO, UPS, etc.) on Odoo Delivery Orders.",
    "author": "Custom",
    "depends": ["base", "stock"],
    "data": [
        "views/carrier_shipment_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "application": False,
}
