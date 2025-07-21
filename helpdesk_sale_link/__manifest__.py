{
    "name": "Helpdesk Sale Order Link",
    "version": "1.0",
    "depends": ["helpdesk", "sale_management"],
    "author": "ChatGPT",
    "category": "Custom",
    "description": "Link Sale Orders to Helpdesk Tickets with smart button",
    "data": [
        "views/helpdesk_ticket_views.xml",
        "views/helpdesk_ticket_action.xml",
        "views/helpdesk_sale_link_actions.xml",
        "actions.xml",
    ],
    "installable": True,
    "application": False,
}
