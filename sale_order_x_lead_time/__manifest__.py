
{
    'name': 'SO Lead Time from Delivery',
    'version': '17.0.1.0.0',
    'summary': 'Computes lead time (days) between Sale Order date and Delivery date_done',
    'description': 'Adds a computed field x_lead_time to Sale Orders, calculated as the number of days between date_order and the latest date_done in related stock pickings. Auto-computes for old and new orders.',
    'author': 'Karl Areglado',
    'category': 'Sales',
    'depends': ['sale', 'stock'],
    'data': [],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'post_init_hook': 'post_init_hook',
}
