{
    'name': 'Sale Helpdesk Link (Fixed)',
    'version': '1.1',
    'depends': ['sale', 'helpdesk'],
    'author': 'ChatGPT',
    'category': 'Custom',
    'data': [
        'views/sale_order_views.xml',
        'views/helpdesk_ticket_views.xml',
        'views/helpdesk_ticket_action.xml',
    ],
    'installable': True,
    'application': False,
}
