{
    "name": "Carrier Shipment Integration",
    "version": "1.0",
    "category": "Inventory/Delivery",
    "summary": "Track shipments (UPS, XPO) from Delivery Orders",
    "description": "Adds Track Shipment button and per-carrier API credentials (UPS/XPO).",
    "author": "Custom",
    "depends": ["base", "stock", "delivery"],
    "data": [
        "views/delivery_carrier_views.xml",
        "views/stock_picking_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
