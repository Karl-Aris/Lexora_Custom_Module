{
    "name": "Helpdesk BCC Extension",
    "version": "1.0",
    "depends": ["helpdesk", "mail"],
    "author": "Karl Areglado",
    "category": "Helpdesk",
    "data": ['views/helpdesk_ticket_views.xml',
            'views/mail_message_bcc_views.xml'
            ],
    "description": "Custom module to handle BCC in helpdesk tickets.",
    "installable": True,
    "application": False,
}
