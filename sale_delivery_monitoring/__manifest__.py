{
    "name": "Sale Delivery Monitoring",
    "version": "1.0",
    "depends": ["sale_management"],
    "author": "Custom",
    "category": "Sales",
    "description": "Track shipments and monitor EDD in Sale Orders",
    "data": [
        "views/sale_order_views.xml",
        "data/cron.xml"
    ],
    "installable": True,
    "application": False
}
