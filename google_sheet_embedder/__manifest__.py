{
    "name": "Google Sheet Embedder",
    "version": "1.1",
    "summary": "Embed editable Google Sheet iframe in Odoo",
    "category": "Tools",
    "depends": ["base", "web"],
    "data": [
        "views/x_google_dashboard_form_inherit.xml"
    ],
    "assets": {
        "web.assets_backend": [
            "google_sheet_embedder/static/src/js/html_frame_widget.js"
        ]
    },
    "installable": True,
    "application": False
}