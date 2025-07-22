{
    'name': 'Product Kits',
    'version': '1.0',
    'summary': 'Manage Product by product configurations',
    'category': 'Inventory',
    'author': 'Chris Mark Cifra',
    'depends': ['base', 'product', 'website'], 
    'data': [
        'security/ir.model.access.csv',
        'views/product_kits_views.xml',
        'views/website_templates.xml',
    ],
    'installable': True,
    'application': True,
}
