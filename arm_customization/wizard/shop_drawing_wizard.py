# -*- coding: utf-8 -*-
#############################################################################
#    Alhodood Technologies.
#
#    Copyright (C) 2024-TODAY Alhodood Technologies(<https://www.alhodood.com>)
#    Author: Alhodood Technologies(<https://www.alhodood.com>)
#
#    You can modify it under the terms of the GNU Affero General Public License (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License (AGPL v3) for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import fields, models, _
from odoo.exceptions import UserError


class ShopDrawingWizard(models.TransientModel):
    _name = 'shop.drawing.wizard'
    _description = 'Shop Drawing'

    comment = fields.Text(string="Comments", required=1)
    command_date = fields.Date(string="Command Date", default=fields.date.today())
    submitted_date = fields.Date(string="Submitted Date", default=fields.date.today())

    def action_submitted(self):
        project_task = self.env['project.task'].browse(self.env.context['active_id'])
        if self.env.context.get('task_type') == 'shop_drawing':
            if self.env.context.get('type') == 'reject':
                project_task.shop_drawing_reject = True
                revision = 'Revision' + str(project_task.revision_shop_drawing_count)
                project_task.shop_drawing_type = 'revision'
                self.env['shop.drawing.line'].create({
                    'submitted_date': self.submitted_date,
                    'command_date': self.command_date,
                    'comments': self.comment,
                    'task_id': project_task.id,
                    'type': 'revision',
                    'revision': revision,
                    'revision_shop_drawing_count': project_task.revision_shop_drawing_count,
                })
                project_task.revision_shop_drawing_count = project_task.revision_shop_drawing_count + 1
            if self.env.context.get('type') == 'approve':
                revision = 'Revision' + str(project_task.revision_shop_drawing_count)
                project_task.shop_drawing_approve = True
                project_task.shop_drawing_type = 'approved'
                self.env['shop.drawing.line'].create({
                    'submitted_date': self.submitted_date,
                    'command_date': self.command_date,
                    'comments': self.comment,
                    'task_id': project_task.id,
                    'type': 'approve',
                    'revision': revision,
                    'revision_shop_drawing_count': project_task.revision_shop_drawing_count,
                })
        if self.env.context.get('task_type') == 'design':
            if self.env.context.get('type') == 'reject':
                revision = 'Revision' + str(project_task.revision_design_count)
                project_task.design_type = 'revision'
                self.env['design.line'].create({
                    'submitted_date': self.submitted_date,
                    'command_date': self.command_date,
                    'comments': self.comment,
                    'task_id': project_task.id,
                    'type': 'revision',
                    'revision': revision,
                    'revision_shop_drawing_count': project_task.revision_design_count,
                })
                project_task.revision_design_count = project_task.revision_design_count + 1
            if self.env.context.get('type') == 'approve':
                revision = 'Revision' + str(project_task.revision_design_count)
                project_task.design_type = 'approved'
                self.env['design.line'].create({
                    'submitted_date': self.submitted_date,
                    'command_date': self.command_date,
                    'comments': self.comment,
                    'task_id': project_task.id,
                    'type': 'approve',
                    'revision': revision,
                    'revision_shop_drawing_count': project_task.revision_design_count,
                })
        if self.env.context.get('task_type') == 'material_sub':
            if self.env.context.get('type') == 'reject':
                revision = 'Revision' + str(project_task.revision_material_sub_count)
                project_task.material_sub_type = 'revision'
                self.env['material.submission.line'].create({
                    'submitted_date': self.submitted_date,
                    'command_date': self.command_date,
                    'comments': self.comment,
                    'task_id': project_task.id,
                    'type': 'revision',
                    'revision': revision,
                    'revision_shop_drawing_count': project_task.revision_material_sub_count,
                })
                project_task.revision_material_sub_count = project_task.revision_material_sub_count + 1
            if self.env.context.get('type') == 'approve':
                revision = 'Revision' + str(project_task.revision_material_sub_count)
                project_task.material_sub_type = 'approved'
                self.env['material.submission.line'].create({
                    'submitted_date': self.submitted_date,
                    'command_date': self.command_date,
                    'comments': self.comment,
                    'task_id': project_task.id,
                    'type': 'approve',
                    'revision': revision,
                    'revision_shop_drawing_count': project_task.revision_material_sub_count,
                })
        if self.env.context.get('task_type') == 'sample_sub':
            if self.env.context.get('type') == 'reject':
                revision = 'Revision' + str(project_task.revision_sample_sub_count)
                project_task.sample_sub_type = 'revision'
                self.env['sample.submission.line'].create({
                    'submitted_date': self.submitted_date,
                    'command_date': self.command_date,
                    'comments': self.comment,
                    'task_id': project_task.id,
                    'type': 'revision',
                    'revision': revision,
                    'revision_shop_drawing_count': project_task.revision_sample_sub_count,
                })
                project_task.revision_sample_sub_count = project_task.revision_sample_sub_count + 1
            if self.env.context.get('type') == 'approve':
                revision = 'Revision' + str(project_task.revision_sample_sub_count)
                project_task.sample_sub_type = 'approved'
                self.env['sample.submission.line'].create({
                    'submitted_date': self.submitted_date,
                    'command_date': self.command_date,
                    'comments': self.comment,
                    'task_id': project_task.id,
                    'type': 'approve',
                    'revision': revision,
                    'revision_shop_drawing_count': project_task.revision_sample_sub_count,
                })


class ShopDrawingSubmittedWizard(models.TransientModel):
    _name = 'shop.drawing.submitted.wizard'
    _description = 'Shop Drawing Submit'

    submitted_date = fields.Date(string="Submitted Date", default=fields.date.today())

    def action_submitted(self):
        project_task = self.env['project.task'].browse(self.env.context['active_id'])
        if self.env.context.get('task_type') == 'shop_drawing':
            project_task.shop_drawing_type = 'submitted'
            project_task.shop_drawing_submitted_date = self.submitted_date
        if self.env.context.get('task_type') == 'design':
            project_task.design_type = 'submitted'
            project_task.shop_design_submitted_date = self.submitted_date
        if self.env.context.get('task_type') == 'material_sub':
            project_task.material_sub_type = 'submitted'
            project_task.shop_material_sub_submitted_date = self.submitted_date
        if self.env.context.get('task_type') == 'sample_sub':
            project_task.sample_sub_type = 'submitted'
            project_task.shop_sample_sub_submitted_date = self.submitted_date


class QAQCStatusWizard(models.TransientModel):
    _name = 'qa.qc.status.wizard'
    _description = 'QaQcStatusWizard'

    submitted_date = fields.Date(string="Submitted Date", default=fields.date.today())
    fail_type = fields.Selection([('fabrication_issue','Fabrication Issue'),('operation_issue','Operation Issue'),('engineering_issue','Engineering Issue')],string="Issue",required=True)
    reason = fields.Text(string="Reason")
    user_id = fields.Many2one('res.users',string="User",default=lambda self: self.env.user)


    def action_submitted(self):
        project_task = self.env['project.task'].browse(self.env.context['active_id'])
        if self.env.context.get('task_type') == 'qa_qc_fail':
            self.env['qa.qc.status.line'].create({
                'submitted_date': self.submitted_date,
                'fail_type': self.fail_type,
                'reason': self.reason,
                'task_id': project_task.id,
                'user_id':self.user_id.id
            })
            project_task.qa_qc_status = 'fail'

        if self.env.context.get('task_type') == 'wir_fail':
            self.env['wir.status.line'].create({
                'submitted_date': self.submitted_date,
                'fail_type': self.fail_type,
                'reason': self.reason,
                'task_id': project_task.id,
                'user_id':self.user_id.id
            })
            project_task.wir_status = 'fail'
