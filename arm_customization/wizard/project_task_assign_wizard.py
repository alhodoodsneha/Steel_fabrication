from odoo import api, models, fields


class ProjectTaskAssignWizard(models.TransientModel):
    _name = 'project.assign.wizard'
    _description = "Project Assign To"

    assign_to = fields.Many2many('res.users','assign_to',string='Assign To',domain=lambda self: [('groups_id', '=', self.env.ref('arm_customization.group_estimation_user').id)])

    def action_assign_to(self):
        project_task = self.env['project.task'].browse(self.env.context['active_id'])
        project_task.write({'user_ids': [(6, 0, self.assign_to.ids)]})
        project_task.assigned_to_done = True
        activity_type_id = self.env.ref('mail.mail_activity_data_todo').id  # Refers to "To Do" activity type
        for rec in self.assign_to:
            project_task.activity_schedule(
                activity_type_id=activity_type_id,
                user_id=rec.id,
                summary='Please review and estimate the project task',
                date_deadline=project_task.date_deadline
            )

