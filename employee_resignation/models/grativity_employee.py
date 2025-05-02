from odoo import fields, models, api, _
from dateutil.relativedelta import relativedelta


class EmployeeGratuity(models.Model):
    _name = 'employee.gratuity'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Gratuity'
    _rec_name = 'employee_id'

    user_id = fields.Many2one('res.users', string='User', tracking=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", tracking=True)
    last_working_day = fields.Date(string='Last Working Day', tracking=True)
    employee_resignation = fields.Many2one('employee.resignation', string="Resignation", tracking=True)
    joining_date = fields.Date(string="Join Date", tracking=True)
    wage = fields.Monetary('Wage', tracking=True)
    gratuity = fields.Monetary(string='Gratuity', compute="_compute_gratuity")
    company_id = fields.Many2one('res.company', string="Employee", related='employee_id.company_id', tracking=True)
    currency_id = fields.Many2one(string="Currency", related='company_id.currency_id', readonly=True)

    def _compute_gratuity(self):
        for rec in self:
            if rec.wage and rec.last_working_day and rec.joining_date:
                years_of_service = relativedelta(rec.last_working_day, rec.joining_date).years
                if years_of_service < 1:
                    rec.gratuity = 0.0
                elif 1 <= years_of_service <= 5:
                    daily_wage = rec.wage / 30  # 30 days in a month
                    rec.gratuity = daily_wage * 21 * years_of_service
                else:
                    daily_wage = rec.wage / 30
                    gratuity_for_first_five_years = daily_wage * 21 * 5
                    gratuity_for_additional_years = daily_wage * 30 * (years_of_service - 5)
                    rec.gratuity = gratuity_for_first_five_years + gratuity_for_additional_years
            else:
                rec.gratuity = 0.0
