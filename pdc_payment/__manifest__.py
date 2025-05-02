# -*- coding: utf-8 -*-
{
    'name': 'PDC Payment',
    'version': '17.0.1.0.0',
    'category': 'Invoices & Payments',
    'summary': 'PDC Payment Customization',
    'description': 'PDC Payment Customization',
    'depends': [
        'account','account_group_payable_receivable'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/pdc_payment.xml',
        'wizard/pdc_reason.xml',
        'wizard/pdc_receive_reason.xml',
        'wizard/pdc_receive_reason_hold.xml',
    ],
    'assets': {},
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
