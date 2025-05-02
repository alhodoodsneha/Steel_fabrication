from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class EmployeeResignation(models.Model):
    _name = 'employee.resignation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Resignation'
    _rec_name = 'employee_id'

    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, tracking=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", related='user_id.employee_id', tracking=True)
    company_id = fields.Many2one('res.company', string="Employee", related='employee_id.company_id', tracking=True)
    department_id = fields.Many2one('hr.department', string="Department", related='employee_id.department_id',
                                    tracking=True)
    state = fields.Selection(
        [('new', 'NEW'), ('submit', 'SUBMIT'), ('first_approve', 'FIRST APPROVAL'), ('approved', 'APPROVED'),
         ('reject', 'Reject')],
        string="state",
        default='new', tracking=True)
    resignation_date = fields.Date(string="Resignation Date", tracking=True)
    request_date = fields.Date(string="Requested Date", tracking=True)
    notice_period = fields.Integer(string="Notice Period", related='employee_id.notice_period', tracking=True)
    notice_period_type = fields.Selection([('day', 'Day'), ('month', 'Month')],
                                          related='employee_id.notice_period_type', tracking=True)
    last_working_day = fields.Date(string='Last Working Day', compute='_compute_last_working_date', tracking=True)
    reason = fields.Text(string="Reason", tracking=True)
    reject_reason = fields.Text(string="Reject Reason", tracking=True)
    is_reject = fields.Boolean(string='rejected', default=False)
    manager = fields.Many2one('hr.employee', string="Manger", related='employee_id.parent_id', tracking=True)
    _is_first_approver = fields.Boolean(string="1st approver", default=False, compute='_compute_is_1st_approver')
    _is_second_approver = fields.Boolean(string="2nd approver", default=False, compute='_compute_is_2nd_approver')
    employee_gratuity_ids = fields.One2many('employee.gratuity', 'employee_resignation', string="employee gratuity")
    _gratuity_calculated = fields.Boolean(string="gratuity calculated", default=False)

    @api.depends('notice_period', 'notice_period_type', 'resignation_date')
    def _compute_last_working_date(self):
        for rec in self:
            if rec.resignation_date and rec.notice_period and rec.notice_period_type:
                if rec.notice_period_type == 'day':
                    rec.last_working_day = rec.resignation_date + timedelta(days=rec.notice_period)
                elif rec.notice_period_type == 'month':
                    last_working_date = rec.resignation_date + relativedelta(months=rec.notice_period)
                    rec.last_working_day = last_working_date
                else:
                    rec.last_working_day = False
            else:
                rec.last_working_day = False

    def _compute_is_1st_approver(self):
        for rec in self:
            if self.env.user.id == rec.manager.sudo().user_id.id:
                rec._is_first_approver = True
            else:
                rec._is_first_approver = False

    def _compute_is_2nd_approver(self):
        for rec in self:
            hr_manager = self.env['res.users'].search([('groups_id', '=', self.env.ref('hr.group_hr_manager').id),
                                                       ('groups_id', '!=', self.env.ref('base.user_admin').id)],
                                                      limit=1)
            if self.env.user.id == hr_manager.id:
                rec._is_second_approver = True
            else:
                rec._is_second_approver = False

    def submit_application(self):
        self.state = 'submit'
        self.request_date = fields.Date.today()
        if self.manager:
            subject = f"Resignation Application Submitted: {self.employee_id.name}"
            body = f"""
                    <p>Hello {self.manager.sudo().name},</p>
                    <p>The employee {self.employee_id.name} has submitted a resignation application on {self.request_date}.</p>
                     <p><strong>Reason for Resignation:</strong> {self.reason}</p>
                    <p>Please review and approve the resignation request.</p>
                    <p>Best Regards,</p>
                    <p>{self.env.user.name}</p>
                    """
            # Create the email
            mail_values = {
                'subject': subject,
                'body_html': body,
                'email_to': self.manager.sudo().user_id.email
            }
            # Send the email
            mail = self.env['mail.mail'].sudo().create(mail_values)
            mail.send()
        else:
            raise UserError("Manager not found for this employee.")

    def first_approve(self):
        self.state = 'first_approve'
        hr_manager = self.env['res.users'].search([('groups_id', '=', self.env.ref('hr.group_hr_manager').id),
                                                   ('groups_id', '!=', self.env.ref('base.user_admin').id)],
                                                  limit=1)
        if hr_manager:
            hr_subject = f"Resignation Application Awaiting Second Approval: {self.employee_id.name}"
            hr_body = f"""
                <p>Hello {hr_manager.name},</p>
                <p>The employee {self.employee_id.name} has submitted a resignation application.</p>
                <p>Their resignation has been approved by {self.manager.name}.</p>
                <p>Please review and approve the resignation request.</p>
                <p>Best Regards,</p>
                <p>{self.env.user.name}</p>
                """

            # Send email to HR manager
            mail_values_hr = {
                'subject': hr_subject,
                'body_html': hr_body,
                'email_to': f"{hr_manager.email}, {self.employee_id.user_id.email}",
            }
            mail_hr = self.env['mail.mail'].sudo().create(mail_values_hr)
            mail_hr.send()

    def second_approve(self):
        self.state = 'approved'
        if not self.notice_period or not self.notice_period_type:
            raise UserError("Please Configure Employee Notice Period")
        self.resignation_date = fields.Date.today()
        subject = f"Resignation Application Approved: {self.employee_id.name}"
        body = f"""
                <p>Hello {self.employee_id.name},</p>
                <p>Your resignation application has been fully approved.</p>
                <p>Best Regards,</p>
                <p>{self.env.user.name}</p>
            """
        mail_values_employee = {
            'subject': subject,
            'body_html': body,
            'email_to': self.employee_id.user_id.email,
        }
        mail_employee = self.env['mail.mail'].sudo().create(mail_values_employee)
        mail_employee.send()

    def calculate_gratuity(self):
        if not self.employee_id.sudo().joining_date:
            raise UserError("Please Configure Employee Join Date In Employee Form")
        hr_contract = self.env['hr.contract'].sudo().search(
            [('state', '=', 'open'), ('employee_id', '=', self.employee_id.id)],limit=1)
        self.env['employee.gratuity'].sudo().create({
            'employee_id': self.employee_id.id,
            'user_id': self.employee_id.user_id.id,
            'last_working_day': self.last_working_day,
            'employee_resignation': self.id,
            'joining_date': self.employee_id.sudo().joining_date,
            'wage': hr_contract.wage
        })

    def reject_reason_add(self):
        self.state = 'reject'
        return {
            'name': 'Rejection Feedback',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'rejection.resignation.wizard',
            'target': 'new',
            'context': {
                'active_id': self.id,
            }
        }

    def reject_reason_add_hr(self):
        self.state = 'reject'
        return {
            'name': 'Rejection Feedback',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'rejection.resignation.wizard',
            'target': 'new',
            'context': {
                'active_id': self.id,
            }
        }
