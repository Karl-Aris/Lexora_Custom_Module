{
    "name": "Fix BCC in Composer",
    "version": "17.0.1.0.0",
    "summary": "Ensures BCC emails are sent when using mail_composer_cc_bcc",
    "category": "Mail",
    "depends": ["mail_composer_cc_bcc", "mail"],
    "data": [
        "views/mail_compose_message_view.xml",
        "views/mail_mail_views.xml",
        
    ],
    "installable": True
}
