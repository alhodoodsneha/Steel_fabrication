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

import io
import base64
from odoo import api, fields, models, _
from odoo.tools.misc import xlsxwriter
from odoo.exceptions import UserError


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    def action_generate_sif(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('WPS REPORT')
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 35)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:I', 15)
        worksheet.set_column('J:J', 15)
        worksheet.set_column('K:K', 15)
        border_format = workbook.add_format({
            'border': 1,
            'font_size': 10,
            'align': 'center',
            'bold': True
        })
        header_format = workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True})
        text_format = workbook.add_format({'font_size': 10, 'align': 'left'})
        number_format = workbook.add_format({'font_size': 10, 'align': 'right'})
        month = self.date_start.strftime('%B')
        year_mn = self.date_start.strftime('%Y')
        row_height = 20
        worksheet.merge_range('A1:J1', 'Establishment : AL RUAYA AL MUTAKAMILAH METAL CONST .IND LLC 0000001911696', header_format)
        worksheet.merge_range('A2:J2', 'MOL ID No :-   1911696', header_format)
        worksheet.merge_range('A3:J3', f'PAYROLL FOR THE MONTH OF {month} {year_mn}', header_format)
        worksheet.merge_range('A5:A6', 'Sl.No', border_format)
        worksheet.merge_range('B5:B6', 'NAME OF THE EMPLOYEE', border_format)
        worksheet.merge_range('C5:C6', 'WORK PERMIT NO (8 DIGIT NO)', border_format)
        worksheet.merge_range('D5:D6', 'PERSONAL NO (14 DIGIT NO)', border_format)
        worksheet.merge_range('E5:E6', 'BANK NAME', border_format)
        worksheet.merge_range('F5:F6', 'FAB CARD NO (16 DIGITS) / LULU MONEY CARD (15 DIGITS) / IBAN (23 DIGITS)', border_format)
        worksheet.merge_range('G5:G6', 'NO OF DAYS ABSENT', border_format)
        worksheet.merge_range('H5:J5', "Employee's Net Salary", border_format)
        worksheet.write(5,7, "Fixed Portion Content", border_format)
        worksheet.write(5,8, "Variable Portion", border_format)
        worksheet.write(5,9, "Total Payment", border_format)
        row = 6
        count= 0
        for slip_id in self.slip_ids:
            worksheet.set_row(row, row_height)
            count = count + 1
            col=0
            worksheet.write(row, col, count,border_format)
            col = col + 1
            worksheet.write(row, col, slip_id.employee_id.name,border_format)
            col = col + 1
            if slip_id.employee_id.permit_no:
                worksheet.write(row, col, slip_id.employee_id.permit_no,border_format)
            else:
                worksheet.write(row, col,' ',border_format)
            col = col + 1
            worksheet.write(row, col, slip_id.employee_id.personal_no,border_format)
            col = col + 1
            if slip_id.employee_id.bank_account_id and slip_id.employee_id.bank_account_id.bank_id:
                worksheet.write(row, col, slip_id.employee_id.bank_account_id.bank_id.name,border_format)
            else:
                worksheet.write(row, col,' ',border_format)
            col = col + 1
            worksheet.write(row, col, slip_id.employee_id.agent_routing_id,border_format)
            col = col + 1
            unpaid_worked_day = slip_id.input_line_ids.filtered(lambda wd: wd.code == 'UNPAID')
            unpaid_leave_days = 0
            if unpaid_worked_day:
                unpaid_leave_days = unpaid_worked_day.amount
            worksheet.write(row, col, unpaid_leave_days,border_format)
            col = col + 1
            basic_salary = slip_id.contract_id.wage
            worksheet.write(row, col, basic_salary,border_format)
            col = col + 1
            if slip_id.line_ids.filtered(lambda line: line.code == 'NET'):
                net_salary = slip_id.line_ids.filtered(lambda line: line.code == 'NET').total
                variable_salary = net_salary - basic_salary
                worksheet.write(row, col, variable_salary,border_format)
            col = col + 1
            if slip_id.line_ids.filtered(lambda line: line.code == 'NET'):
                net_salary = slip_id.line_ids.filtered(lambda line: line.code == 'NET').total
                worksheet.write(row, col, net_salary,border_format)
            row = row + 1
        if self.date_start:
            report_month = self.date_start.strftime('%B')
            report_year = self.date_start.strftime('%Y')
            report_name = f'WPS_{report_month}_{report_year}.xlsx'
        else:
            report_name = 'WPS_Report.xlsx'
        workbook.close()
        output.seek(0)
        # Download the generated file
        attachment = self.env['ir.attachment'].create({
            'name': report_name,
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self'
        }
