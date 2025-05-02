from odoo import api, models, fields, _
from odoo.exceptions import UserError
import base64
import io
from odoo.tools.misc import xlsxwriter


class ProjectTask(models.Model):
    _inherit = 'project.task'

    _is_estimation_task = fields.Boolean(string="Estimation Task", default=False)
    _is_work_task = fields.Boolean(string="Work Order Task", default=False)
    total_estimation = fields.Float(string="Estimation Total", compute='_compute_total_estimation', tracking=True)
    sequence_code = fields.Char(string="Sequence")
    estimation_status = fields.Selection(
        [('under_estimation', 'Under Estimation'), ('approve', 'Approve Estimation'),
         ('refuse_estimation', 'Refuse Estimation'), ('cancel', 'Cancel')],
        string="Estimation Status", default='under_estimation', tracking=True)
    refuse_reason = fields.Text(string="Refuse Reason", tracking=True)
    revision_count = fields.Integer(string="Revision Count", default=0)
    _revision_task = fields.Boolean(string="Revision Task", default=False)
    estimation_parent_id = fields.Many2one('project.task', string="Estimation Parent")
    crm_lead_id = fields.Many2one('crm.lead', string="Enquiry", related='project_id.crm_lead_id', tracking=True)
    is_completed = fields.Boolean(string='Complete', default=False)
    boq_material_ids = fields.One2many('boq.material', 'task_id', string="BOQ", tracking=True)
    assigned_to_done = fields.Boolean(string="Assigned To done", default=False)
    parent_task = fields.Many2one('project.task', string="parent Task")
    revision_name = fields.Char(string="Revision name")
    ohp = fields.Integer(string="OHP %")
    bd_fee = fields.Integer(string="BD fee %")
    actual_cost = fields.Float(string="Actual Cost", compute='_compute_actual_cost')
    start_date = fields.Date(string='Start Date', related="project_id.date_start")
    end_date = fields.Date(string='End Date', related="project_id.date")
    crm_sequence_code = fields.Char(string='CRM', related="crm_lead_id.sequence_code")
    job_name = fields.Char(string='Job Name', related="crm_lead_id.job_name")
    job_status = fields.Selection([('job_in_hand', 'Job In Hand'), ('tender', 'Tender')],
                                  related='crm_lead_id.job_status', string="Job Status")
    enquiry_date = fields.Date('Enquiry Date', related='crm_lead_id.enquiry_date')
    partner_id = fields.Many2one('res.partner',
                                 string='Customer', recursive=True, tracking=True, compute='_compute_partner_id',
                                 store=True,
                                 domain="['|', ('company_id', '=?', company_id), ('company_id', '=', False)]")

    wrk_start_date = fields.Date(string="Start Date")
    wrk_end_date = fields.Date(string="End Date")
    actual_wrk_start_date = fields.Date(string="Actual Work Start date")
    actual_wrk_end_date = fields.Date(string="Actual Work End Date")
    delay = fields.Integer(string="Delay", compute="_compute_delay_project")
    stage_wk = fields.Selection(
        [('waiting', 'Engineering'), ('qa_ist', 'QA/QC'), ('production', 'Production'), ('qa_qc', 'QA/QC'),
         ('delivered', 'Delivery'),
         ('invoiced', 'Invoiced')], string="Stage Work", default='waiting')
    is_mrp_created = fields.Boolean(string="Is Work Order Created", default=False)
    is_eng_task = fields.Boolean(string="Is eng task", default=False)
    is_qa_qc_task = fields.Boolean(string="Is Qa task", default=False)
    job_wrk_name = fields.Char(string="Work Name")
    job_eng_name = fields.Char(string="Engineering Job Name")
    job_qa_name = fields.Char(string="QA/Qc Name")
    p_qty = fields.Float(string="Qty")
    p_uom = fields.Many2one('uom.uom', string='UOM')
    w_product = fields.Many2one('product.product', string="Product")
    w_boq = fields.Many2one('project.boq.line', string="Product Boq")
    wr_project = fields.Many2one('project.task', 'Work Order')
    wr_qa_project = fields.Many2one('project.task', 'Work Order')
    date_created = fields.Date(string="Work Create Date")
    stage_engineering = fields.Selection([('waiting', 'Waiting'), ('completed', 'Completed')], default='waiting',
                                         string='Stage')
    stage_qa = fields.Selection([('waiting', 'Waiting'), ('completed', 'Completed')], default='waiting',
                                string='Stage')
    assemble_line_ids = fields.One2many('assemble.qty', 'work_id', string="Assemble Line")
    wr_progress = fields.Float(string="Work Progress(%)", compute="_compute_total_progress")
    mrp_id = fields.Many2one('mrp.production', string="Mrp")
    shop_drawing_type = fields.Selection(
        [('pending', 'Pending'), ('submitted', 'Submitted'), ('approved', 'Approved'), ('revision', 'revision')],
        string="Shop Drawing Type", default='pending', tracking=True)
    design_type = fields.Selection(
        [('pending', 'Pending'), ('submitted', 'Submitted'), ('approved', 'Approved'), ('revision', 'revision')],
        string="Design Type", default='pending', tracking=True)
    material_sub_type = fields.Selection(
        [('pending', 'Pending'), ('submitted', 'Submitted'), ('approved', 'Approved'), ('revision', 'revision')],
        string="Material Submission Type", default='pending', tracking=True)
    sample_sub_type = fields.Selection(
        [('pending', 'Pending'), ('submitted', 'Submitted'), ('approved', 'Approved'), ('revision', 'revision')],
        string="Sample Submission Type", default='pending', tracking=True)
    shop_drawing_approve = fields.Boolean(string="Approve Shop Drawing", tracking=True)
    shop_drawing_reject = fields.Boolean(string="Reject Shop Drawing", tracking=True)
    revision_shop_drawing_count = fields.Integer(string="Shop Drawing Revision Count", default=0)
    revision_design_count = fields.Integer(string="Shop Design Count", default=0)
    revision_material_sub_count = fields.Integer(string="Material Submission Count", default=0)
    revision_sample_sub_count = fields.Integer(string="Sample Submission Count", default=0)
    stage_type = fields.Selection(
        [('shop_drawing', 'Shop Drawing'), ('design', "Design"), ('material', 'Material'), ('sample', 'Sample'),
         ('material_request', 'Material Request'), ('fabrication', 'Fabrication'), ('production', 'Production'),
         ('delivered', 'Delivered'), ('mir_approved', 'MIR Approved'), ('eraction', 'Eraction'), ('qa_qc', 'QA/Qc'),
         ('wir', 'WIR'), ('built_submission', 'Built Submission'), ('invoiced', 'Invoiced'),
         ('estimation', 'Estimation')], string="Stage Type",
        related='stage_id.stage_type', tracking=True)

    shop_drawing_submitted_date = fields.Date(string="Submitted date", tracking=True)
    shop_design_submitted_date = fields.Date(string="Submitted date", tracking=True)
    shop_material_sub_submitted_date = fields.Date(string="Submitted date", tracking=True)
    shop_sample_sub_submitted_date = fields.Date(string="Submitted date", tracking=True)
    shop_drawing_line_ids = fields.One2many('shop.drawing.line', 'task_id', string="Shop Drawing Line", tracking=True)
    design_line_ids = fields.One2many('design.line', 'task_id', string="Design Line", tracking=True)
    material_submission_line_ids = fields.One2many('material.submission.line', 'task_id',
                                                   string="Material Submission Line", tracking=True)
    sample_submission_line_ids = fields.One2many('sample.submission.line', 'task_id',
                                                 string="Sample Submission Line", tracking=True)
    site_measurement = fields.Selection([('no', 'No'), ('yes', 'Yes'), ('partial', 'Partial')],
                                        string='Site Measurement', default='no', tracking=True)
    mir_status = fields.Selection([('mir_approve', 'MIR Approve'), ('mir_reject', 'MIR Reject')], string="MIR Status",
                                  tracking=True)
    eraction_status = fields.Selection(
        [('drawing', 'Drawing'), ('installation', 'Installation'), ('completed', 'Completed')],
        string="Eraction Status", tracking=True)
    qa_qc_status = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')], string="Qa/Qc Status", tracking=True)
    wir_status = fields.Selection([('pass', 'Pass'), ('fail', 'Fail')], string="WIR Status", tracking=True)
    qa_qc_line_ids = fields.One2many('qa.qc.status.line', 'task_id', string="QA/Qc Lines")
    wir_line_ids = fields.One2many('wir.status.line', 'task_id', string="WIR Lines")
    settlement_status = fields.Selection([('pending', 'Pending'), ('submit', 'Submitted')], string="Settlement",
                                         default='pending')

    def action_approve_shop_drawing(self):
        return {
            'name': 'Approve Shop Drawing',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'shop.drawing.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        'type': 'approve',
                        'task_type': 'shop_drawing'
                        }
        }

    def action_reject_shop_drawing(self):
        return {
            'name': 'Reject Shop Drawing',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'shop.drawing.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        'type': 'reject',
                        'task_type': 'shop_drawing'
                        }
        }

    def action_submit_shop_drawing(self):
        return {
            'name': 'Drawing Submitted',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'shop.drawing.submitted.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        'task_type': 'shop_drawing'
                        }
        }

    def action_submit_design(self):
        return {
            'name': 'Drawing Submitted',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'shop.drawing.submitted.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        'task_type': 'design'
                        }
        }

    def action_approve_design(self):
        return {
            'name': 'Approve Design',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'shop.drawing.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        'type': 'approve',
                        'task_type': 'design'
                        }
        }

    def action_reject_design(self):
        return {
            'name': 'Reject Design',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'shop.drawing.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        'type': 'reject',
                        'task_type': 'design'
                        }
        }

    def action_submit_material_sub(self):
        return {
            'name': 'Material Submitted',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'shop.drawing.submitted.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        'task_type': 'material_sub'
                        }
        }

    def action_approve_material_sub(self):
        return {
            'name': 'Approve Material Submission',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'shop.drawing.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        'type': 'approve',
                        'task_type': 'material_sub'
                        }
        }

    def action_reject_material_sub(self):
        return {
            'name': 'Reject Material Submission',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'shop.drawing.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        'type': 'reject',
                        'task_type': 'material_sub'
                        }
        }

    def action_submit_sample_sub(self):
        return {
            'name': 'Sample Submitted',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'shop.drawing.submitted.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        'task_type': 'sample_sub'
                        }
        }

    def action_approve_sample_sub(self):
        return {
            'name': 'Approve Material Submission',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'shop.drawing.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        'type': 'approve',
                        'task_type': 'sample_sub'
                        }
        }

    def action_reject_sample_sub(self):
        return {
            'name': 'Reject Material Submission',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'shop.drawing.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        'type': 'reject',
                        'task_type': 'sample_sub'
                        }
        }

    def action_pass_qa_qc(self):
        self.qa_qc_status = 'pass'

    def action_fail_qa_qc(self):
        return {
            'name': 'Fail Wizard',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'qa.qc.status.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        'task_type': 'wir_fail'
                        }
        }

    def action_pass_wir(self):
        self.wir_status = 'pass'

    def action_fail_wir(self):
        return {
            'name': 'Fail Wizard',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'qa.qc.status.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        'task_type': 'wir_fail'
                        }
        }

    def action_submit_base_settlement(self):
        self.settlement_status = 'submit'

    def action_mir_approve(self):
        self.mir_status = 'mir_approve'

    def action_mir_reject(self):
        self.mir_status = 'mir_reject'

    def action_create_invoice(self):
        stage = self.env['project.task.type'].search(
            [('stage_type', '=', 'invoiced')])
        if not stage:
            raise UserError(_("Please Configure stage Invoice"))
        self.stage_id = stage.id
        account_admin_group = self.env.ref('account.group_account_manager')
        account_admins = self.env['res.users'].search([('groups_id', 'in', account_admin_group.id)])
        if not account_admins:
            raise UserError("Account Managers Not Found !!")
        if self.env.user.email:
            for user in account_admins:
                if user.email:
                    subject = f"Create Invoice of {self.name} -  for project {self.project_id.name} "
                    body = f"""
                                <p>Dear {user.name},</p>
                                <p>An invoice needs to be created for the following Work order:</p>
                                <ul>
                                    <li><strong>Project:</strong> {self.project_id.name} - {self.job_name}</li>
                                    <li><strong>Work:</strong> {self.job_wrk_name}</li>
                                </ul>
                                <p>Please proceed with the necessary actions.</p>
                                <p>Best Regards, {self.env.user.name}</p>
                            """
                    mail_values = {
                        'subject': subject,
                        'body_html': body,
                        'email_to': user.email,
                        'email_from': self.env.user.email,
                    }
                    self.env['mail.mail'].create(mail_values).send()

    @api.onchange('stage_type')
    def _onchange_stage_type(self):
        if self.stage_type == 'production' and not self.assemble_line_ids:
            raise UserError(_("Please Add Assembly Lines !!"))
        if self.stage_type == 'delivered':
            not_delivered_lines = self.assemble_line_ids.filtered(lambda l: l.item_status != 'delivered')
            if not_delivered_lines:
                raise UserError(
                    "You cannot change the stage to 'Delivered' because some items are not delivered.")

    def unlink(self):
        if not self.env.user.has_group('arm_customization.group_delete_user'):
            raise UserError(_("You do not have the access to delete records !!"))
        else:
            return super(ProjectTask, self).unlink()

    @api.depends('assemble_line_ids', 'assemble_line_ids.qty', 'assemble_line_ids.state')
    def _compute_total_progress(self):
        for rec in self:
            rec.wr_progress = 0.0
            if rec.assemble_line_ids:
                approved_lines = rec.assemble_line_ids.filtered(lambda line: line.item_status == 'delivered')
                if approved_lines:
                    total_qty = sum(rec.assemble_line_ids.mapped('qty'))
                    approved_qty = sum(approved_lines.mapped('qty'))
                    rec.wr_progress = ((approved_qty / total_qty) * 100) if total_qty > 0 else 0.0

    @api.depends('wrk_start_date', 'wrk_end_date', 'actual_wrk_start_date', 'actual_wrk_end_date')
    def _compute_delay_project(self):
        for rec in self:
            if rec.wrk_start_date and rec.wrk_end_date and rec.actual_wrk_start_date and rec.actual_wrk_end_date:
                planned_duration = (rec.wrk_end_date - rec.wrk_start_date).days
                actual_duration = (rec.actual_wrk_end_date - rec.actual_wrk_start_date).days
                rec.delay = int(planned_duration - actual_duration)
            else:
                rec.delay = 0
    @api.depends('boq_material_ids','boq_material_ids.subtotal')
    def _compute_total_estimation(self):
        for rec in self:
            if rec.boq_material_ids:
                rec.total_estimation = sum(line.subtotal for line in rec.boq_material_ids)
            else:
                rec.total_estimation = 0.0

    @api.depends('total_estimation', 'ohp', 'bd_fee')
    def _compute_actual_cost(self):
        for record in self:
            percentage_reduction = (record.ohp + record.bd_fee) / 100.0
            record.actual_cost = record.total_estimation * (1 - percentage_reduction)

    def action_approve_estimation(self):
        if not self.boq_material_ids:
            raise UserError("Please add at least one Boq line")
        self.estimation_status = 'approve'
        if self._revision_task:
            parent_task = self.estimation_parent_id
        else:
            parent_task = self
        order_lines = []
        for line in self.boq_material_ids:
            order_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'product_uom_qty': line.quantity,
                'price_unit': line.unit_price,
                'name': line.description,
                'product_uom': line.uom.id,
            }))
        sale_order = self.env['sale.order'].sudo().create({
            'partner_id': self.partner_id.id,
            'parent_task': parent_task.id,
            'estimated_task': self.id,
            'estimated_amount': self.total_estimation,
            'order_line': order_lines,
            'user_id': self.crm_lead_id.sudo().user_id.id,
        })
        self.crm_lead_id.sudo().quotation_type = 'quote_submitted'

    def action_approve_revision_estimation(self):
        self.estimation_status = 'approve'
        if self._revision_task:
            parent_task = self.estimation_parent_id
        else:
            parent_task = self
        order_lines = []
        for line in self.boq_material_ids:
            order_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'product_uom_qty': line.quantity,
                'price_unit': line.unit_price,
                'name': line.description,
                'product_uom': line.uom.id,
            }))
        sale_order = self.env['sale.order'].sudo().create({
            'partner_id': self.partner_id.id,
            'parent_task': parent_task.id,
            'estimated_task': self.id,
            'estimated_amount': self.total_estimation,
            'order_line': order_lines,
        })
        self.crm_lead_id.sudo().quotation_type = 'quote_submitted'

    def action_assign_to(self):
        return {
            'name': 'Assign To',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'project.assign.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        }
        }

    def action_cancel_estimation(self):
        self.estimation_status = 'cancel'
        self.state = '1_canceled'
        self.crm_lead_id.sudo().quotation_type = 'cancel'
        return {
            'name': 'Estimation Rejection Feedback',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'estimation.rejection.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        'cancel': True,
                        }
        }

    def action_refuse_estimation(self):
        self.estimation_status = 'refuse_estimation'
        self.state = '1_canceled'
        self.revision_count = self.revision_count + 1
        if self.estimation_parent_id:
            estimation_parent_id = self.estimation_parent_id
        else:
            estimation_parent_id = self
        # sequence_est_task = self.env['ir.sequence'].next_by_code('project.task.estimation')
        subtask = self.env['project.task'].create({
            'name':estimation_parent_id.name + '- R'+str(self.revision_count),
            'revision_name': f'Revision - {self.revision_count}',
            'project_id': self.project_id.id,
            'revision_count': self.revision_count,
            'estimation_parent_id': estimation_parent_id.id,
            'date_deadline': self.date_deadline,
            'parent_task': self.id,
            '_revision_task': True,
            'user_ids': [(6, 0, [user.id for user in self.user_ids])],
            'partner_id': self.partner_id.id,
            'boq_material_ids': [(0, 0, {
                'sequence': line.sequence,
                'product_id': line.product_id.id,
                'description': line.description,
                'quantity': line.quantity,
                'uom': line.uom.id,
                'unit_price': line.unit_price,
            }) for line in self.boq_material_ids],

        })
        return {
            'name': 'Estimation Rejection Feedback',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'estimation.rejection.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        }
        }

    def action_refuse_revision_estimation(self):
        self.estimation_status = 'refuse_estimation'
        self.state = '1_canceled'
        self.revision_count = self.revision_count + 1
        if self.estimation_parent_id:
            estimation_parent_id = self.estimation_parent_id
        else:
            estimation_parent_id = self
        # sequence_est_task = self.env['ir.sequence'].next_by_code('project.task.estimation')
        subtask = self.env['project.task'].create({
            'name': estimation_parent_id.name + '- R'+str(self.revision_count),
            'revision_name': f'Revision - {self.revision_count}',
            'project_id': self.project_id.id,
            'revision_count': self.revision_count,
            'estimation_parent_id': estimation_parent_id.id,
            '_revision_task': True,
            'parent_task': self.id,
            'date_deadline': self.date_deadline,
            'user_ids': [(6, 0, [user.id for user in self.user_ids])],
            'partner_id': self.partner_id.id,
            'boq_material_ids': [(0, 0, {
                'sequence': line.sequence,
                'product_id': line.product_id.id,
                'description': line.description,
                'quantity': line.quantity,
                'uom': line.uom.id,
                'unit_price': line.unit_price,
            }) for line in self.boq_material_ids],
        })
        return {
            'name': 'Estimation Rejection Feedback',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'estimation.rejection.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        }
        }

    def action_open_related_sale_order(self):
        sale_order_ids = self.env['sale.order'].search([('parent_task', '=', self.id)])
        return {
            'name': 'Sale Order',
            'view_type': 'list',
            'view_mode': 'list,form',
            'res_model': 'sale.order',
            'domain': [('id', 'in', sale_order_ids.ids)],
            'type': 'ir.actions.act_window',
        }

    def action_related_sale_order(self):
        sale_order_ids = self.env['sale.order'].search([('estimated_task', '=', self.id)])
        return {
            'name': 'Sale Order',
            'view_type': 'list',
            'view_mode': 'list,form',
            'res_model': 'sale.order',
            'domain': [('id', 'in', sale_order_ids.ids)],
            'type': 'ir.actions.act_window',
        }

    def action_export_boq_item(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Import Products')
        headers = ['Sl No','Product','Item Description','UOM', 'Qty', 'Unit Rate','Price']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)
        workbook.close()
        output.seek(0)
        attachment = self.env['ir.attachment'].create({
            'name': 'Import Products.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self'
        }

    def action_boq_upload_item(self):
        return {
            'name': 'BOQ Upload',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'bulk.item.upload.task',
            'target': 'new',
            'context': {
                'active_id': self.id,
            }
        }

    def action_create_mrp(self):
        self.env['mrp.production'].sudo().create({
            'product_id': self.w_product.id,
            'product_qty': self.p_qty,
            'product_uom_id': self.p_uom.id,
        })

    def action_completed_engineering(self):
        sequence_qa_qc_task = self.env['ir.sequence'].next_by_code('project.task.qa')
        qa_qc_user = self.env['res.users'].search(
            [('groups_id', '=', self.env.ref('arm_customization.group_qa_qc_manager').id),
             ('groups_id', '!=', self.env.ref('base.user_admin').id),
             ('groups_id', 'not in', self.env.ref('base.group_system').id)])
        qa_qc_task = self.env['project.task'].sudo().create({
            'name': sequence_qa_qc_task,
            'job_qa_name': 'Design Verification -' + self.wr_project.name,
            'sequence_code': sequence_qa_qc_task,
            'partner_id': self.partner_id.id,
            'user_ids': [(6, 0, [user.id for user in qa_qc_user])] if qa_qc_user else False,
            'project_id': self.project_id.id,
            'wr_qa_project': self.wr_project.id,
            'is_qa_qc_task': True,
            'description': 'Please Upload the Assembly Number in - ' + self.wr_project.name + 'also add timesheet and complete the Qa/Qc  work in ' + self.wr_project.name
        })
        self.stage_engineering = 'completed'
        self.wr_project.stage_wk = 'qa_ist'
        self.state = '1_done'

    def action_completed_qa(self):
        if self.wr_qa_project.stage_wk == 'qa_ist':
            if not self.wr_qa_project.assemble_line_ids:
                raise UserError("Please add Assemble lines")
            mrp = self.env['mrp.production'].sudo().create({
                'product_id': self.wr_qa_project.w_product.id,
                'product_qty': self.wr_qa_project.p_qty,
                'product_uom_id': self.wr_qa_project.p_uom.id,
                'work_order_id': self.wr_qa_project.id
            })
            self.stage_qa = 'completed'
            self.wr_qa_project.stage_wk = 'production'
            self.state = '1_done'
        else:
            all_factors_positive = all(line.state != 'draft' for line in self.wr_qa_project.assemble_line_ids)
            if not all_factors_positive:
                raise UserError("Please Verify all lines !!")
            self.wr_qa_project.stage_wk = 'delivered'
            self.stage_qa = 'completed'
            self.state = '1_done'

    def action_assemble_upload_item(self):
        return {
            'name': 'Assemble Upload',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'assemble.item.upload',
            'target': 'new',
            'context': {
                'active_id': self.id,
            }
        }

    def action_export_assemble_item(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Import Assemble')
        headers = ['Assembly Mark', 'No', 'Name', 'Profile', 'Net Area for one', 'Net Area for all',
                   'Net Weight For one', 'Net Weight for all']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)
        workbook.close()
        output.seek(0)
        attachment = self.env['ir.attachment'].create({
            'name': 'Assemble Items.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self'
        }

    def action_material_request(self):
        return {
            'name': 'Material Request',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'material.requisition.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        'default_work_order': self.id,
                        }
        }

    def action_open_related_mrq(self):
        return {
            'name': 'Material Request',
            'view_type': 'list',
            'view_mode': 'list,form',
            'res_model': 'material.request.item',
            'domain': [('task_id', '=', self.id)],
            'type': 'ir.actions.act_window',
        }
