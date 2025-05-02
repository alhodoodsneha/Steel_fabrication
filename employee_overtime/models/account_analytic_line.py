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
from datetime import datetime
from odoo.exceptions import UserError


class TimesheetLine(models.Model):
    _inherit = 'account.analytic.line'

    state_approve = fields.Selection(
        [('waiting_for_approval', 'Waiting For Approval'), ('approve', 'Approved'), ('refuse', 'Refuse')],
        string='State', default='waiting_for_approval')

    is_project_manager = fields.Boolean(string='Manager', compute='_compute_is_project_manager')

    @api.depends('project_id', 'state_approve', 'date', 'unit_amount', )
    def _compute_is_project_manager(self):
        for rec in self:
            if rec.project_id:
                if self.env.user.id == rec.project_id.user_id.id:
                    rec.is_project_manager = True
                else:
                    rec.is_project_manager = False
            else:
                rec.is_project_manager = False

    def approve_timesheet(self):
        self.state_approve = 'approve'
        if self.employee_id.resource_calendar_id:
            daily_hours = self.employee_id.resource_calendar_id.hours_per_day
            total_hours = sum(self.env['account.analytic.line'].search([
                ('employee_id', '=', self.employee_id.id),
                ('state_approve', '=', 'approve'),
                ('date', '=', self.date)]).mapped('unit_amount'))
            if total_hours > daily_hours:
                approved_existing_overtime = self.env['hr.employee.overtime'].search([
                    ('employee_id', '=', self.employee_id.id), ('state', '=', 'approved'),
                    ('date_assigned', '=', self.date)
                ])
                if approved_existing_overtime:
                    overtime_hours = self.unit_amount - daily_hours
                    self.env['hr.employee.overtime'].create({
                        'employee_id': self.employee_id.id,
                        'date_assigned': self.date,
                        'overtime_hours': overtime_hours,
                    })
                else:
                    overtime_hours = total_hours - daily_hours
                    existing_overtime = self.env['hr.employee.overtime'].search([
                        ('employee_id', '=', self.employee_id.id), ('state', '=', 'draft'),
                        ('date_assigned', '=', self.date)
                    ])
                    if existing_overtime:
                        existing_overtime.overtime_hours = overtime_hours
                    else:
                        self.env['hr.employee.overtime'].create({
                            'employee_id': self.employee_id.id,
                            'date_assigned': self.date,
                            'overtime_hours': overtime_hours,
                        })

    def reject_timesheet(self):
        self.state_approve = 'refuse'

    def write(self, vals):
        if self.state_approve in ['approve', 'refuse']:
            raise UserError(_("You do not have the rights to update this record!!"))
        else:
            res = super(TimesheetLine, self).write(vals)
            return res

    def unlink(self):
        if self.state_approve in ['approve', 'refuse']:
            raise UserError(_("You do not have the rights to delete this record!!"))
        return super(TimesheetLine, self).unlink()
