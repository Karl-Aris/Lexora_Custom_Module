
{
    "name": "Google Sheet Embedder",
    "version": "1.0",
    "depends": ["base", "web"],
    "author": "Your Name",
    "category": "Tools",
    "description": "Embed Google Sheets using iframe widget.",
    "data": [
        "views/x_google_dashboard_form_inherit.xml"
    ],
    "assets": {
        "web.assets_backend": [
            "/google_sheet_embedder/static/src/js/html_frame_widget.js"
        ]
    },
    "installable": True,
    "application": False,
}
