from odoo import fields, models, api, _


class RejectionResignationFeedback(models.TransientModel):
    _name = 'rejection.resignation.wizard'
    _description = "Rejection Feedback"

    feedback = fields.Text('Feedback')

    def action_add_feedback(self):
        request_id = self.env['employee.resignation'].search([('id', '=', self.env.context['active_id'])])
        request_id.reject_reason = self.feedback
