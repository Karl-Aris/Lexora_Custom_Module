{
    "name": "Sale Order Favorites Grouping Custom",
    "version": "1.0",
    "author": "Custom",
    "category": "Sales",
    "depends": ["sale", "web"],
    "data": [
        "views/sale_order_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/sale_order_favorites_grouping_custom/static/src/xml/search_favorites_menu.xml",
        ],
    },
    "installable": True,
    "application": False,
}
