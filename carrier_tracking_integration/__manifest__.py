{
    'name': 'FedEx Tracking (REST API)',
    'version': '1.0',
    'category': 'Delivery',
    'summary': 'Track FedEx shipments via REST API',
    'description': 'Integrates FedEx REST API for shipment tracking in Sale Orders.',
    'depends': ['sale_management', 'delivery'],
    'data': [
        'views/sale_order_views.xml',
        'views/delivery_carrier_views.xml',
    ],
    'installable': True,
    'application': False,
}
