# -*- coding: utf-8 -*-
{
    'name': 'X Return',
    'version': '1.0.0',
    'summary': 'Automatically copy stock.move.line entries into x.return for WH/INT/RETURN references',
    'description': 'Creates x.return model and automatically copies move lines whose reference contains WH/INT/RETURN. Provides tree/form views and menu action filtered to those references.',
    'author': 'Karl Areglado',
    'depends': ['stock', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/x_return_views.xml',
        'views/x_return_action.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
