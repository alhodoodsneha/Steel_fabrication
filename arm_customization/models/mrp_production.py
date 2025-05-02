from odoo import api, models, fields, _
from odoo.exceptions import UserError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    work_order_id = fields.Many2one('project.task', string="Work Order")
    assemble_id = fields.Many2one('assemble.qty', string="Assemble")

    def action_create_qa_qc(self):
        if self.work_order_id:
            sequence_qa_qc_task = self.env['ir.sequence'].next_by_code('project.task.qa')
            qa_qc_user = self.env['res.users'].search(
                [('groups_id', '=', self.env.ref('arm_customization.group_qa_qc_manager').id),
                 ('groups_id', '!=', self.env.ref('base.user_admin').id),
                 ('groups_id', 'not in', self.env.ref('base.group_system').id)])
            if not qa_qc_user:
                raise UserError(_("No QA/QC User Found !!"))
            qa_qc_task = self.env['project.task'].sudo().create({
                'name': sequence_qa_qc_task,
                'job_qa_name': 'Verification -' + self.work_order_id.name,
                'sequence_code': sequence_qa_qc_task,
                'partner_id': self.work_order_id.partner_id.id,
                'user_ids': [(6, 0, [user.id for user in qa_qc_user])] if qa_qc_user else False,
                'project_id': self.work_order_id.project_id.id,
                'wr_qa_project': self.work_order_id.id,
                'is_qa_qc_task': True,
                'description': 'Please verify the Assembly Number in - ' + self.work_order_id.name + 'also add timesheet and complete the Qa/Qc  work in ' + self.work_order_id.name
            })
            self.work_order_id.stage_wk = 'qa_qc'

    def action_material_request(self):
        return {
            'name': 'Material Request',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'material.requisition.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        'default_work_order': self.work_order_id.id,
                        'default_mrp_id': self.id,
                        }
        }

    def action_open_related_mrq(self):
        return {
            'name': 'Material Request',
            'view_type': 'list',
            'view_mode': 'list,form',
            'res_model': 'material.request.item',
            'domain': [('mrp_id', '=', self.id)],
            'type': 'ir.actions.act_window',
        }