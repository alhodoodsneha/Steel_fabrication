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
    'name': 'Recruitment Customization',
    'version': '17.0.0.0.0',
    'category': 'Hr',
    'summary': 'Recruitment Customization',
    'description': 'Recruitment Customization',
    'author': 'Alhodood Technologies',
    'depends': [
        'hr','hr_recruitment'
    ],
    'data': [
        'data/ir_sequence.xml',
        'views/hr_applicant.xml',
        'views/offer_letter_report.xml',
        'views/joining_letter_emp_report.xml',
        'views/ir_action_report.xml',
    ],
    'demo': [
    ],
    'assets': {},
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
