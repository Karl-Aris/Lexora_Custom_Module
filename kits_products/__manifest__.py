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
        'views/product_kits.xml',
        'views/kits_config.xml',
       
        
    ],
    'installable': True,
    'application': True,
}
