{
    "name": "Delivery Monitoring (EDD & Status Buckets)",
    "version": "17.0.1.0",
    "summary": "Track EDD, auto-bucket missed deliveries, and streamline follow-ups",
    "author": "Your Company",
    "license": "LGPL-3",
    "depends": ["stock"],  # uses stock.picking & carrier_tracking_ref
    "data": [
        "data/ir_cron.xml",
        "views/stock_picking_views.xml",
    ],
    "application": False,
    "installable": True,
}
