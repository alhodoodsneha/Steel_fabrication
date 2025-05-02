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


class HrEmployeeOverTime(models.Model):
    _name = 'hr.employee.overtime'
    _description = 'Employee OverTime'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'sequence'

    sequence = fields.Char(string='Sequence', copy=False, readonly=True,
                           default=lambda self: _('New'), tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    date_assigned = fields.Date(string="Date")
    overtime_hours = fields.Float(string='Overtime Hours', required=True)
    state = fields.Selection([
        ('draft', 'Waiting For Approval'),
        ('approved', 'Approved'),
        ('refused', 'Refused')
    ], default='draft', string='Status')

    is_public_holiday = fields.Boolean(string='Is Public', compute='_compute_public_holiday',store=True)
    is_done_payslip = fields.Boolean(string='Paid',default=False)
    reject_reason = fields.Text(string="Reject Reason")
    is_employee_manager = fields.Boolean(string='Manager', compute='_compute_is_employee_manager')

    @api.depends('employee_id', 'state')
    def _compute_is_employee_manager(self):
        for rec in self:
            if rec.employee_id and rec.employee_id.parent_id:
                if self.env.user.id == rec.employee_id.parent_id.user_id.sudo().id:
                    rec.is_employee_manager = True
                else:
                    rec.is_employee_manager = False
            else:
                rec.is_employee_manager = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('sequence', _('New')) == _('New'):
                vals['sequence'] = self.env['ir.sequence'].next_by_code('hr.employee.overtime')
        return super().create(vals_list)

    @api.depends('date_assigned')
    def _compute_public_holiday(self):
        for rec in self:
            if rec.date_assigned:
                public_holidays = self.env['resource.calendar.leaves'].search([
                    ('date_from', '<=', rec.date_assigned),
                    ('date_to', '>=', rec.date_assigned),
                ])
                if public_holidays:
                    rec.is_public_holiday = True
                else:
                    rec.is_public_holiday = False
            else:
                rec.is_public_holiday = False

    def approve_overtime(self):
        self.state = 'approved'

    def refuse_over_time(self):
        return {
            'name': 'Rejection Feedback',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'rejection.overtime.wizard',
            'target': 'new',
            'context': {
                'active_id': self.id,
            }
        }
