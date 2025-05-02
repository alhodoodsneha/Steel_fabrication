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
from odoo import api, fields, models, _

from odoo.exceptions import UserError
from datetime import date

class UpdateTimesheetWizard(models.TransientModel):
    _name = 'update.timesheet.wizard'
    _description = 'Update Timesheet Wizard'

    today_date = fields.Date(string='Date', default=date.today(), readonly=True)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    timesheet_lines = fields.One2many(
        'update.timesheet.line.wizard',
        'wizard_id',
        string='Timesheet Lines'
    )

    def action_update_timesheet(self):
        for line in self.timesheet_lines:
            if line.hours <= 0:
                raise UserError("Hours must be greater than zero!")
            self.env['account.analytic.line'].create({
                'employee_id': line.employee_id.id,
                'project_id': self.project_id.id,
                'unit_amount': line.hours,
                'date': self.today_date,
            })


class UpdateTimesheetLineWizard(models.TransientModel):
    _name = 'update.timesheet.line.wizard'
    _description = 'Update Timesheet Line Wizard'

    wizard_id = fields.Many2one('update.timesheet.wizard', string='Wizard')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    hours = fields.Float(string='Hours', required=True)