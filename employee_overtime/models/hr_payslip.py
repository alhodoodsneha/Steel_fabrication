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


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    employee_overtime_ids = fields.Many2many('hr.employee.overtime','rel_emp_over_time',
                                    string='Overtime')

    public_overtime_ids = fields.Many2many('hr.employee.overtime','public_emp_over_time',
                                             string='Overtime')

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        """
        function used for writing overtime record in payslip
        input tree.

        """
        res = super(HrPayslip, self).get_worked_day_lines(contracts, date_to, date_from)
        overtime_type = self.env.ref('employee_overtime.hr_over_time_salary')
        contract = self.contract_id
        overtime_ids = self.env['hr.employee.overtime'].search([('employee_id', '=', self.employee_id.id),
                                                               ('date_assigned', '>=', date_from),
                                                               ('date_assigned', '<=', date_to),
                                                               ('is_public_holiday', '=', False),
                                                               ('state', '=', 'approved'),
                                                               ('is_done_payslip', '=', False)])
        public_overtime_ids = self.env['hr.employee.overtime'].search([('employee_id', '=', self.employee_id.id),
                                                                ('date_assigned', '>=', date_from),
                                                                ('date_assigned', '<=', date_to),
                                                                ('is_public_holiday', '=', True),
                                                                ('state', '=', 'approved'),
                                                                ('is_done_payslip', '=', False)])
        if overtime_ids:
            hours_overtime = sum(overtime_ids.mapped('overtime_hours'))
            self.employee_overtime_ids = overtime_ids
            input_data = {
                'name': overtime_type.name,
                'code': overtime_type.code,
                'sequence': 15,
                'contract_id': contract.id,
                'number_of_days': 0.0,
                'number_of_hours':hours_overtime
            }
            res.append(input_data)
        if  public_overtime_ids:
            public_hours_overtime = sum(public_overtime_ids.mapped('overtime_hours'))
            p_overtime_type = self.env.ref('employee_overtime.hr_public_over_time_salary')
            self.public_overtime_ids = public_overtime_ids
            p_input_data = {
                'name': p_overtime_type.name,
                'code': p_overtime_type.code,
                'sequence': 16,
                'contract_id': contract.id,
                'number_of_days': 0.0,
                'number_of_hours': public_hours_overtime
            }
            res.append(p_input_data)
        return res


    def action_payslip_done(self):
        for recd in self.employee_overtime_ids:
            recd.is_done_payslip = True
        for rec in self.public_overtime_ids:
            rec.is_done_payslip = True
        return super(HrPayslip, self).action_payslip_done()
