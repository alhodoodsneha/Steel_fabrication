# -*- coding: utf-8 -*-
{
    'name': 'Invoice Report Customization',
    'version': '17.0.0.0.2',
    'category': 'Accounting & Finance',
    'summary': 'Invoice Report',
    'description': 'Invoice Report Customization',
    'depends': [
        'account','l10n_ae'
    ],
    'data': [
        'views/res_company.xml',
        # 'views/account_move.xml',
        'views/report_invoice_custom.xml'
    ],
    'assets': {},
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
