{
    'name': 'Sale Delivery Tracking (Other Information)',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Adds delivery tracking fields to Other Information tab in Sale Orders',
    'description': """
Adds custom delivery tracking fields to the Other Information tab of the Sale Order form.
    """,
    'author': 'Carl Aris Areglado',
    'depends': ['sale'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
