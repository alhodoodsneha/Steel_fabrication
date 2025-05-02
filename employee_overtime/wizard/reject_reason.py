from odoo import fields, models, api, _


class RejectionOvertimeFeedback(models.TransientModel):
    _name = 'rejection.overtime.wizard'
    _description = "Rejection Feedback"

    feedback = fields.Text('Feedback')

    def action_add_feedback(self):
        request_id = self.env['hr.employee.overtime'].search([('id', '=', self.env.context['active_id'])])
        request_id.reject_reason = self.feedback
        request_id.state = 'refused'
