{
    "name": "Deductions",
    "version": "1.0",
    "summary": "Manage Deductions",
    "author": {
        "email": "aljon.garde1197@gmail.com"
      },
    "depends": ["base", "sale", "purchase", "product", "mail", "quality"],
    'data': [
        'security/ir.model.access.csv',
        'data/deduction_sequence.xml',
        'views/deduction_views.xml',
    ],
    "installable": True,
    "application": True,
}
