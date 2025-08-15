{
    'name': 'Sale Delivery Tracking Extension',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Adds delivery tracking fields and filters to Sales Orders',
    'description': 'Adds custom delivery tracking fields to the Other Information tab of Sales Orders and provides search filters.',
    'author': 'Custom',
    'depends': ['sale_management'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
