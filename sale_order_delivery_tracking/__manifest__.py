# -*- coding: utf-8 -*-
{
    "name": "Sale Order Tracking (Enhanced, FedEx-ready)",
    "version": "17.0.1.0",
    "summary": "Real-time tracking via carrier APIs (FedEx first), with chatter history & cron",
    "license": "LGPL-3",
    "category": "Sales/Sales",
    "depends": ["sale_management", "mail", "stock"],
    "data": [
        "views/sale_order_views.xml",
        "data/ir_cron.xml",
    ],
    "installable": True,
    "application": False,
}
