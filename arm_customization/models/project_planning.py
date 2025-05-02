from odoo import models, fields, api,_
from odoo.exceptions import UserError

class ProjectPlanningType(models.Model):
    _name = 'project.planning.type'
    _description = 'Project Planning'
    _rec_name = 'name'
    name = fields.Char(string="Planning Type")


class ProjectPlanning(models.Model):
    _name = 'project.planning'
    _description = 'Project Planning'
    _rec_name = 'display_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True, tracking=True)
    type = fields.Many2one('project.planning.type', string='Type', required=True, tracking=True)
    project = fields.Many2one('project.project', string='Project', domain="[('_work_order_prj', '=', True)]",
                              required=True, tracking=True)
    start_date = fields.Date(string="Start Date", required=True, index=True, copy=False, tracking=True)
    end_date = fields.Date(string="End Date", required=True, index=True, copy=False, tracking=True)
    display_name = fields.Char(
        string="Display Name",
        compute="_compute_display_name",
        store=True,
        tracking=True
    )
    actual_start_date = fields.Date(string="Actual Start date", tracking=True)
    actual_end_date = fields.Date(string="Actual End Date", tracking=True)
    is_verified = fields.Boolean(string="Is Verify",default=False)
    status = fields.Selection([('draft','Draft'),('verify','Verify')],default='draft')

    @api.depends('name', 'project')
    def _compute_display_name(self):
        for record in self:
            project_name = record.project.name if record.project else ""
            record.display_name = f"{record.name or ''} - {project_name}"

    def unlink(self):
        if not self.env.user.has_group('arm_customization.group_delete_user'):
            raise UserError(_("You do not have the access to delete records !!"))
        else:
            return super(ProjectPlanning, self).unlink()

    def action_verify_planning(self):
        self.is_verified = True
        self.status = 'verify'
