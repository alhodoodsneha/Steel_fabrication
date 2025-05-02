from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    joining_date = fields.Date(string="Join Date")
    last_working_day = fields.Date(string="Last Working Date")
    notice_period = fields.Integer(string="Notice Period")
    notice_period_type = fields.Selection([('day','Day'),('month','Month')],default='day')