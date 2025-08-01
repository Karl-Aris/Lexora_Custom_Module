# -*- coding: utf-8 -*-
{
    'name': 'Authorize.Net Credit Card Fee',
    'version': '1.1',
    'summary': 'Adds a 3.5% fee before Authorize.Net payment is processed.',
    'description': 'Automatically adds a 3.5% fee line to Sales Orders before payment if Authorize.Net is selected.',
    'author': 'Custom for Fabs',
    'depends': ['sale', 'payment_authorize_net', 'website_sale'],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
