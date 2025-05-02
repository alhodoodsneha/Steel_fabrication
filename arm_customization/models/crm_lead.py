from odoo import api, models, fields, _
from odoo.exceptions import UserError


class Lead(models.Model):
    _inherit = 'crm.lead'

    project_job_id = fields.Many2one('project.project', string='Related Job')
    assigned = fields.Boolean(string="Assigned", default=False)
    quotation_type = fields.Selection([
        ('no_action_taken', 'No Action Taken'), ('waiting_for_estimation', 'Waiting For Estimation'),
        ('estimation_completed', 'Estimation Completed'), ('quote_submitted', 'Quote Submitted'),
        ('approved', 'Approved'),('cancel','Cancel Estimation')
    ], default='no_action_taken', string="Quotation Type")
    project_detail = fields.Text(string="Job Detail")
    enquiry_date = fields.Date('Enquiry Date', default=fields.Date.today)
    date_deadline = fields.Date('Expiry Date', help="Estimate of the date on which the opportunity will be won.")
    sequence_code = fields.Char(string="Sequence Code")
    job_name = fields.Char(string="Job Name")
    job_status = fields.Selection([('job_in_hand','Job In Hand'),('tender','Tender')])

    @api.model
    def create(self, vals):
        res = super(Lead, self).create(vals)
        res.sequence_code = self.env['ir.sequence'].next_by_code('crm.lead')
        return res

    def unlink(self):
        if not self.env.user.has_group('arm_customization.group_delete_user'):
            raise UserError(_("You do not have the access to delete records !!"))
        else:
            return super(Lead, self).unlink()

    def action_assign_to_job_creation(self):
        if not self.job_name:
            raise UserError(_("Please Add the job name"))
        if not self.partner_id:
            raise UserError(_("Please Add the Customer"))
        if not self.date_deadline:
            raise UserError(_("Please Add the Expiry date"))
        estimation_manager = self.env['estimation.team.member'].search([], limit=1)
        if not estimation_manager:
            raise UserError(_("Please Configure the Estimation Team"))
        analytic_plan_id = self.env['account.analytic.plan'].search([('name', '=', 'Projects')])
        if not analytic_plan_id:
            analytic_plan_id = self.env['account.analytic.plan'].create({'name': 'Projects'})
        # sequence = self.env['ir.sequence'].next_by_code('project.project')
        analytic_account = self.env['account.analytic.account'].sudo().create({
            'name': self.sequence_code,
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id,
            'code': self.sequence_code,
            'plan_id': analytic_plan_id.id

        })
        project = self.env['project.project'].sudo().create({
            'name': self.sequence_code,
            'user_id': estimation_manager.team_manager_id.id,
            'job_name': self.job_name,
            'partner_id': self.partner_id.id,
            'crm_lead_id': self.id,
            'allow_timesheets': True,
            'esm_prjct': True,
            'description': self.project_detail,
            'analytic_account_id': analytic_account.id,
            'type_project':'pre_tender',
        })
        # sequence_est_task = self.env['ir.sequence'].next_by_code('project.task.estimation')
        project_task = self.env['project.task'].sudo().create({
            'name': self.sequence_code,
            'revision_name': f'Revision - {0}',
            'sequence_code': self.sequence_code,
            'user_ids': [(6, 0, [estimation_manager.team_manager_id.id])],
            'partner_id': self.partner_id.id,
            'date_deadline' : self.date_deadline,
            'description': self.project_detail,
            'project_id': project.id,
            '_is_estimation_task': True
        })
        activity_type_id = self.env.ref('mail.mail_activity_data_todo').id  # Refers to "To Do" activity type
        project_task.activity_schedule(
            activity_type_id=activity_type_id,
            user_id=estimation_manager.team_manager_id.id,
            summary='Please review and estimate the project task',
            date_deadline = self.date_deadline
        )

        self.write({
            'project_job_id': project.id,
            'assigned': True,
            'quotation_type': 'waiting_for_estimation'
        })

    def action_open_related_job(self):
        if self.assigned and self.project_job_id:
            return {
                'name': 'Related Job',
                'view_type': 'list',
                'view_mode': 'list,form',
                'res_model': 'project.project',
                'domain': [('id', '=', self.project_job_id.id)],
                'type': 'ir.actions.act_window',
            }
    def action_open_related_task(self):
        if self.assigned and self.project_job_id:
            return {
                'name': 'Related Task',
                'view_type': 'list',
                'view_mode': 'list,form',
                'res_model': 'project.task',
                'domain': [('project_id', '=', self.project_job_id.id)],
                'type': 'ir.actions.act_window',
            }