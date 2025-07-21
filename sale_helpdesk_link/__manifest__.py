{
    'name': 'Sale Helpdesk Link',
    'version': '1.0',
    'depends': ['sale', 'helpdesk'],
    'author': 'ChatGPT',
    'category': 'Custom',
    'data': [
        'views/sale_order_views.xml',
        'views/helpdesk_ticket_views.xml',
    ],
    'installable': True,
    'application': False,
}
