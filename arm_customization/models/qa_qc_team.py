from odoo import models,fields,api


class QaTeamMember(models.Model):
    _name = 'qa.team.member'
    _description = 'QA Team'
    _rec_name = 'name'

    name = fields.Char(string="Name")
    team_manager_id  = fields.Many2one('res.users',string='Engineering Manager',domain=lambda self: [('id', 'in', self._get_group_user_ids())])
    team_member_ids  = fields.Many2many('res.users',string="Members",domain=lambda self: [('id', 'in', self._get_group_qa_user_ids())])


    @api.model
    def _get_group_user_ids(self):
        group = self.env.ref('arm_customization.group_qa_qc_manager')
        return group.users.ids if group else []

    @api.model
    def _get_group_qa_user_ids(self):
        group = self.env.ref('arm_customization.group_qa_qc_user')
        return group.users.ids if group else []