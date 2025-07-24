{
    'name': 'Product Kits',
    'version': '1.0',
    'summary': 'Manage Product by product configurations',
    'category': 'Inventory',
    'author': 'Chris Mark Cifra',
    'depends': ['base', 'product', 'website'], 
    'data': [
        
        'security/product_kits_security.xml',
        'security/ir.model.access.csv',
        'views/product_kits_views.xml',
        'views/website_templates.xml',
        'views/product_kit_import_views.xml',
        'views/product_kit_export_views.xml',
        
    ],
    'installable': True,
    'application': True,
}
