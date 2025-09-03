# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sales Order: Lexora Importation',
    'category': 'Sales',
    'description': """
        Odoo - Lexora Importation
    """,
    "version": "17.0.0.1.1",
    "author": "Jasper Rivera, <j.rivera112214@gmail.com>",
    'depends': ['sale', 'delivery', 'sale_order_processing_lexora', "account"],
    'data': [
        'security/ir.model.access.csv',
        'wizard/sale_order_importation_views.xml',
        'wizard/choose_delivery_carrier_views.xml',
        'wizard/sale_order_upload_result_views.xml',
        'wizard/platform_generic_importation_views.xml',
        'views/sale_order_views.xml',
        'views/sale_menus.xml',
        'views/lexora_sale_order_importation_template_views.xml',
        'data/lexora_sale_order_importation_template_data.xml',
        'data/sale_order_data.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'return_report/static/src/views/**/*',
        ],
    },
    "license": "Other proprietary",
    "installable": True,
    "auto_install": False,
    "application": False,
    "external_dependencies": {"python" : ["pandas"]}

}
