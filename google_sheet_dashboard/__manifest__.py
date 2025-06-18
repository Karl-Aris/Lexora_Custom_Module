{
    "name": "Google Sheet Dashboard",
    "version": "1.0",
    "author": "Karl Areglado",
    "depends": ["web"],
    "category": "Tools",
    "summary": "Embed Google Sheet as a dashboard inside Odoo",
    "description": "A simple module that embeds a published Google Sheet as an iframe-based dashboard in the Odoo backend.",
    "data": ["views/dashboard_view.xml"],
    "assets": {
        "web.assets_backend": [
            "google_sheet_dashboard/static/src/js/google_sheet_dashboard.js",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False
}
