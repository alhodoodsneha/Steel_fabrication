from odoo import api, models, fields


class EstimationRejectionWizard(models.TransientModel):
    _name = 'estimation.rejection.wizard'
    _description = "Estimation Rejection Feedback"

    feedback = fields.Text('Feedback',required=True)

    def action_add_feedback(self):
        project_task = self.env['project.task'].browse(self.env.context['active_id'])
        project_task.refuse_reason = self.feedback

