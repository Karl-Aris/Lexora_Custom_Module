{
    "name": "Helpdesk BCC Support",
    "version": "17.0.1.0.0",
    "summary": "Adds BCC support to Helpdesk emails and chatter",
    "author": "Karl Areglado",
    "category": "Helpdesk",
    "depends": ["mail", "helpdesk"],
    "data": [],
    "assets": {},
    "installable": True,
    "application": False,
    "license": "LGPL-3",
    "post_init_hook": "post_init_hook",
    "pre_init_hook": "pre_init_hook",
    "auto_install": False,
    "data": [
        "views/mail_composer.xml"  # <-- leave this here, but make sure models are initialized first
    ]
}
