{
    "name": "Google Sheet Dashboard",
    "version": "1.0",
    "depends": ["web"],
    "category": "Tools",
    "application": True,
    "data": ["views/dashboard_view.xml"],
    "assets": {
        "web.assets_backend": [
            "google_sheet_dashboard/static/src/js/google_sheet_dashboard.js"
        ]
    }
}
