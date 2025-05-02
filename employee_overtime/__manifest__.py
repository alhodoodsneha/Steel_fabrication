# -*- coding: utf-8 -*-
#############################################################################

#    Alhodood Technologies.
#
#    Copyright (C) 2024-TODAY Alhodood Technologies(<https://www.alhodood.com>)
#    Author: Alhodood Technologies(<https://www.alhodood.com>)
#
#    You can modify it under the terms of the GNU Affero General Public License (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License (AGPL v3) for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
{
    'name': 'Employee Over Time',
    'version': '17.0.0.0.1',
    'category': 'Contact',
    'summary': 'Employee Over Time',
    'description': 'Employee Over Time',
    'author': 'Alhodood Technologies',
    'depends': [
        'hr','hr_payroll_community','hr_timesheet','hr_holidays',
    ],
    'data': [
        'data/ir_sequence.xml',
        'data/hr_overtime_rule.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/employee_hr_overtime.xml',
        'views/account_analytic_account.xml',
        'views/hr_payslip.xml',
        'wizard/update_timesheet.xml',
        'wizard/reject_reason.xml',
    ],
    'demo': [
    ],
    'assets': {},
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
