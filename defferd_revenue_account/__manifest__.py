# -*- coding: utf-8 -*-
{
    'name': 'Deffered Revenue Customization',
    'version': '17.0.1.0.0',
    'category': 'Invoices & Payments',
    'summary': 'Invoice Customization',
    'description': 'Invoice Customization',
    'depends': [
        'account'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/deffered_entry_posting.xml',
        'views/account_move.xml',
        'views/deffered_account_revenue.xml',
        'wizard/deffered_entry_wizard.xml',
    ],
    'assets': {},
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
