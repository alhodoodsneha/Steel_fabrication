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
    'name': 'Attach Contact Documentt',
    'version': '17.0.0.0.0',
    'category': 'Contact',
    'summary': 'Attach Contact Documentt',
    'description': 'Attach Contact Documentt',
    'author': 'Alhodood Technologies',
    'depends': [
        'contacts'
    ],
    'data': [
        'data/ir_sequence.xml',
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/document_type.xml',
        'views/partner_document.xml',
        'views/res_partner.xml',

    ],
    'demo': [
        'data/document_type_demo.xml',
    ],
    'assets': {},
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
