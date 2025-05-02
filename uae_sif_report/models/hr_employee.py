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
from odoo import api, fields, models


class Employee(models.Model):
    _inherit = 'hr.employee'

    employee_unique_id = fields.Char(
        string="Employee Unique ID", size=14,
        help="Employee Unique ID Of Employee")

    personal_no = fields.Char(
        string="Personal No", size=14,
        help="Personal Number")

    agent_routing_id = fields.Char(
        string="Fab Card No", size=23,
        help="Fab Card No of employee")

    employee_account_with_agent = fields.Char(
        string="Employee Account with Agent",
        help="Employee Account with Agent of employee")



