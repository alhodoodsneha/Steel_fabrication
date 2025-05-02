from odoo import api, models, fields, _
import base64
import io
from odoo.tools.misc import xlsxwriter
from odoo.exceptions import UserError
from odoo.tools.populate import compute


class SaleVerifiedOrderLine(models.Model):
    _name = 'sale.verified.order.line'
    _description = 'Sale Verified Line'
    _rec_name = 'name'
    name = fields.Char(string="Name")


class SaleVerifiedLine(models.Model):
    _name = 'sale.verified.line'
    _description = 'Sale Verified Line'
    _rec_name = 'name'

    name = fields.Char(string="Item Name")
    user_id = fields.Many2one('res.users', string="Verified User")
    stage = fields.Selection([('done', 'Done')])
    sale_id = fields.Many2one('sale.order', string="Sale")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _default_new_sale_id(self):
        return self.id if self else False

    estimated_task = fields.Many2one('project.task', string="Estimated Task")
    parent_task = fields.Many2one('project.task', string="parent Task")
    state = fields.Selection(selection_add=[('revision', 'Revision'), ('approve_accounts', 'Approve')])
    old_sale_ids = fields.One2many('sale.order', 'new_sale_id', string="Old Sale Orders",
                                   compute='_compute_parent_task_sale_orders')
    new_sale_id = fields.Many2one('sale.order', string="New Sale Order",
                                  default=lambda self: self._default_new_sale_id())

    estimated_amount = fields.Float(string="Estimated Amount")
    job_reference = fields.Char('Project Name')
    is_created = fields.Boolean(string="Create Project", default=False)
    verified_lines = fields.One2many('sale.verified.line', 'sale_id', string="Verified Lines")
    type_sale = fields.Selection([('lump_sum', 'Lump sum'), ('qty', 'Qty')], string="Type")
    project_id = fields.Many2one('project.project',string="Project",related='estimated_task.project_id')
    crm_id = fields.Many2one('crm.lead',string="Enquiry",related='project_id.crm_lead_id')

    def unlink(self):
        if not self.env.user.has_group('arm_customization.group_delete_user'):
            raise UserError(_("You do not have the access to delete records !!"))
        else:
            return super(SaleOrder, self).unlink()

    def action_refuse_task_estimation(self):
        self.state = 'revision'
        self.estimated_task.estimation_status = 'refuse_estimation'
        self.estimated_task.state = '1_canceled'
        self.estimated_task.revision_count = self.estimated_task.revision_count + 1
        if self.estimated_task.estimation_parent_id:
            estimation_parent_id = self.estimated_task.estimation_parent_id
        else:
            estimation_parent_id = self.estimated_task
        # sequence_est_task = self.env['ir.sequence'].next_by_code('project.task.estimation')
        subtask = self.env['project.task'].create({
            'name': estimation_parent_id.name + '- R'+ str(self.estimated_task.revision_count),
            'revision_name': f'Revision - {self.estimated_task.revision_count}',
            'project_id': self.estimated_task.project_id.id,
            'revision_count': self.estimated_task.revision_count,
            'estimation_parent_id': estimation_parent_id.id,
            'parent_task': self.estimated_task.id,
            'date_deadline': self.estimated_task.date_deadline,
            '_revision_task': True,
            'user_ids': [(6, 0, [user.id for user in self.estimated_task.user_ids])],
            'partner_id': self.estimated_task.partner_id.id,
            'boq_material_ids': [(0, 0, {
                'sequence': line.sequence,
                'product_id': line.product_id.id,
                'description': line.description,
                'quantity': line.quantity,
                'uom': line.uom.id,
                'unit_price': line.unit_price,
            }) for line in self.estimated_task.boq_material_ids],
        })
        return {
            'name': 'Estimation Rejection Feedback',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'estimation.rejection.wizard',
            'target': 'new',
            'context': {'active_id': self.estimated_task.id,
                        }
        }

    @api.depends('parent_task')
    def _compute_parent_task_sale_orders(self):
        for sale_order in self:
            if sale_order.parent_task != sale_order.estimated_task:
                # Find the sale order linked to the parent task
                parent_tasks = []
                current_task = sale_order.estimated_task
                while current_task._revision_task:
                    parent_tasks.append(current_task.parent_task.id)
                    current_task = current_task.parent_task
                parent_sale_order = self.env['sale.order'].search([
                    ('estimated_task', 'in', parent_tasks)
                ])
                sale_order.old_sale_ids = parent_sale_order
            else:
                sale_order.old_sale_ids = False

    def action_export_boq_item(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Import Products')
        headers = ['Product','Item Description','UOM', 'Qty', 'Unit Rate']
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
            'res_model': 'bulk.item.upload',
            'target': 'new',
            'context': {
                'active_id': self.id,
            }
        }

    def action_approve_form_accounts(self):
        self.ensure_one()
        val_list = []
        check_list_ids = self.env['sale.approve.configuration'].sudo().search([])
        if not check_list_ids:
            raise UserError(_("Please Configure Verification Items !!"))
        for rec in check_list_ids:
            val_list.append((0, 0, {
                'name': rec.name,
                'is_verified': False,
            }))
        verify_wizard = self.env['sale.approve.wizard'].sudo().create({
            'sale_order_id': self.id,
            'verification_line_ids': val_list,
        })
        return {
            'name': 'Verification Item',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sale.approve.wizard',
            'res_id': verify_wizard.id,
            'target': 'new',
            'context': {
                'active_id': self.id,
            }
        }

    def action_create_work_order(self):
        if not self.env.user.email:
            raise UserError(_("Please configure your mail id!!"))
        if not self.client_order_ref:
            raise UserError(_("Please Configure Your LPO Number !!"))
        sequence = self.env['ir.sequence'].next_by_code('project.work.sequence')
        order_lines = []
        for line in self.order_line:
            order_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'description': line.name,
                'quantity': line.product_uom_qty,
                'unit_price': line.price_unit,
                'uom': line.product_uom.id,
            }))
        wr_user = self.env['res.users'].search(
            [('groups_id', '=', self.env.ref('arm_customization.group_work_order_manager').id),
             ('groups_id', '!=', self.env.ref('base.user_admin').id),
             ('groups_id', 'not in', self.env.ref('base.group_system').id)
             ], limit=1)
        project = self.estimated_task.project_id
        self.estimated_task.project_id.sudo().write({
            'job_sale_name': self.project_id.job_name,
            'partner_id': self.partner_id.id,
            '_work_order_prj': True,
            'project_total_amount': self.estimated_amount,
            'project_boq_line': order_lines,
            'user_id': wr_user.id
        })
        project.sudo().wrk_sale_order_id = self.sudo().id
        project.sudo().type_project = 'post_tender'
        project.sudo().lpo_number = self.client_order_ref
        users = self.env['res.users'].search(
            [('groups_id', '=', self.env.ref('arm_customization.group_project_plan').id)])
        if users:
            for user in users:
                if user.email:
                    subject = f"New Work Order Created - : {project.sudo().name + '-' + project.sudo().job_sale_name}"
                    body = f"""
                                        <p>Hello {user.sudo().name},</p>
                                        <p>New Work Order - {project.sudo().name + '-' + project.sudo().job_sale_name} is created please plan the project </p>
                                        <p>Best Regards,</p>
                                        <p>{self.env.user.name}</p>
                                        """
                    # Create the email
                    mail_values = {
                        'subject': subject,
                        'body_html': body,
                        'email_from': self.env.user.email,
                        'email_to': user.email,
                    }
                    # Send the email
                    mail = self.env['mail.mail'].sudo().create(mail_values)
                    mail.send()
        self.is_created = True

    def action_invoice_per(self):
        order_lines = self.order_line.filtered(lambda line: line.balanced_percentage > 0.0)
        if not order_lines:
            raise UserError(_("No Pending Invoice Line!!"))
        samp_val_list = []
        for line_id in order_lines:
            samp_val_list.append((0, 0, {
                'name': line_id.name,
                'qty': line_id.product_uom_qty,
                'unit_price': line_id.price_unit,
                'line_id': line_id.id,
                'balanced_percentage': line_id.balanced_percentage,
                'inv_total_amount': line_id.inv_total_amount,
            }))
        verify_wizard = self.env['progress.invoice.creation'].sudo().create({
            'sale_order': self.id,
            'wizard_line_ids': samp_val_list,
        })
        return {
            'name': 'Progress Invoice',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_id': verify_wizard.id,
            'res_model': 'progress.invoice.creation',
            'target': 'new',
            'context': {
                'active_id': self.id,
                'filtered_order_lines': order_lines.ids,
            }
        }

    def action_view_sale_invoice(self):
        account_moves = self.env['account.move'].search([('sale_inv_id', '=', self.id)])
        return {
            'name': 'Invoice',
            'view_type': 'list',
            'view_mode': 'list,form',
            'res_model': 'account.move',
            'domain': [('id', 'in', account_moves.ids)],
            'type': 'ir.actions.act_window',
        }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    invoiced_percentage = fields.Float(string="Invoiced Percentage", default=0.0)
    balanced_percentage = fields.Float(string="Balanced Percentage", default=100.0)
    inv_total_amount = fields.Float(string="Total Amount", compute='_compute_amount_inv_total')
    total_qty_invoiced = fields.Float(string="total qty invoiced",default=0.0)
    total_amount_invoiced = fields.Float(string="total amount invoiced",default=0.0)

    @api.depends('product_uom_qty', 'price_unit')
    def _compute_amount_inv_total(self):
        for rec in self:
            rec.inv_total_amount = rec.product_uom_qty * rec.price_unit
