{
    'name': 'XPO Shipment Integration',
    'version': '17.0.0.0',
    'category': 'Warehouse',
    'summary': 'Integrate XPO shipment tracking into Odoo',
    'description': 'Track XPO shipments from Odoo Delivery Orders',
    'author': 'Custom',
    'depends': ['base', 'stock'],
    'data': [
        'views/xpo_shipment_views.xml',
    ],
    'installable': True,
    'application': False,
}
