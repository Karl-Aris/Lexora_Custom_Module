{
    "name": "Sales: Delivery Monitoring (EDD & Status Buckets)",
    "version": "17.0.1.0",
    "summary": "Track shipment EDD & delivery status on Sales Orders with daily auto-bucketing",
    "author": "Your Company",
    "license": "LGPL-3",
    "depends": ["sale_management"],  # minimum: sale; using sale_management for standard views/actions
    "data": [
        "data/cron_update_delivery_status.xml",
        "views/sale_order_views.xml",
    ],
    "application": False,
    "installable": True,
}
