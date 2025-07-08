# __manifest__.py
{
    'name': "Dealer Portal Order Alert",
    'version': '1.0',
    'depends': ['sale_management', 'mail'],
    'author': "Your Company",
    'category': 'Sales',
    'description': "Sends email notification when a Dealer Portal user confirms an order.",
    'data': [
        'data/email_template.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}