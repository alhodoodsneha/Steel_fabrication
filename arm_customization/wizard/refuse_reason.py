from odoo import api, models, fields


class AssembleRejectionWizard(models.TransientModel):
    _name = 'assemble.rejection.wizard'
    _description = "Assemble Rejection Feedback"

    feedback = fields.Text('Feedback', required=True)

    def action_add_feedback(self):
        project_task = self.env['assemble.qty'].browse(self.env.context['active_id'])
        project_task.comments = self.feedback
        project_task.state = 'refuse'
