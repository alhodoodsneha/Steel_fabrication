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
    'name': 'UAE SIF Report Customization',
    'version': '17.0.0.0.2',
    'category': 'Human Resources',
    'summary': 'SIF Report for UAE',
    'description': 'SIF Report',
    'author': 'Alhodood Technologies',
    'depends': [
        'hr_payroll_community', 'hr_holidays','account'
    ],
    'data': [
            'views/hr_employee.xml',
            'views/hr_payslip_run.xml',
            'views/hr_payslip.xml',
    ],
    'assets': {},
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
