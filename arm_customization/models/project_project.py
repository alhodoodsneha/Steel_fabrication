from odoo import api, models, fields, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class ProjectBOQLine(models.Model):
    _name = 'project.boq.line'
    _description = 'BOQ Line'
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product', string="Product", required=True)
    description = fields.Char(string="Description")
    quantity = fields.Float(string="Qty")
    uom = fields.Many2one('uom.uom', string="UOM")
    unit_price = fields.Float(string="Unit Price")
    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal")
    project_id = fields.Many2one('project.project', string='Project')
    work_order = fields.Many2one('project.task', string="Work Order")
    invoice_percentage = fields.Float(string="Invoice Percentage", default=0, compute='_compute_total_inv_per')
    balance_percentage = fields.Float(string="Balance Percentage", default=100, compute='_compute_total_bal_per')
    total_invoice_amount = fields.Float(string="Total Invoice")
    sub_total_amount_adv = fields.Float(string="sub Total Adv amount", compute='_compute_total_amount_adv')
    sub_total_amount_adv_paid = fields.Float(string="sub Total Adv amount paid")

    @api.depends('project_id.is_adv_created', 'project_id.advance_recovery', 'total_invoice_amount',
                 'project_id.project_total_amount', 'quantity', 'subtotal', 'unit_price')
    def _compute_total_amount_adv(self):
        for rec in self:
            rec.sub_total_amount_adv = 0.0
            if rec.project_id.is_adv_created and not rec.project_id.advance_recovery:
                rec.sub_total_amount_adv = rec.subtotal - (
                        (rec.unit_price * rec.quantity) * rec.project_id.adv_per) / 100

    @api.depends('product_id', 'subtotal', 'project_id.project_total_amount', 'quantity', 'unit_price')
    def _compute_total_inv_per(self):
        for rec in self:
            invoice = self.env['account.move'].search(
                [('project_job_id', '=', rec.project_id.id), ('move_type', '=', 'out_invoice'),
                 ('state', '=', 'posted')])
            if invoice:
                lines = self.env['account.move.line'].search(
                    [('move_id', 'in', invoice.ids), ('boq_line', '=', rec.id)])
                if lines:
                    inv_per = sum(lines.mapped('invoice_per'))
                    if inv_per > 100:
                        rec.invoice_percentage = 100
                    else:
                        rec.invoice_percentage = inv_per
                else:
                    rec.invoice_percentage = 0.0
            else:
                rec.invoice_percentage = 0.0

    @api.depends('product_id', 'subtotal', 'project_id.project_total_amount', 'quantity', 'unit_price')
    def _compute_total_bal_per(self):
        for rec in self:
            if rec.invoice_percentage:
                rec.balance_percentage = 100 - rec.invoice_percentage
            else:
                rec.balance_percentage = 100

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.quantity * record.unit_price


class Project(models.Model):
    _inherit = 'project.project'

    crm_lead_id = fields.Many2one('crm.lead', string="Crm")
    job_name = fields.Char(string="Job Name", related='crm_lead_id.job_name')
    job_sale_name = fields.Char(string="Job Name")
    job_status = fields.Selection([('job_in_hand', 'Job In Hand'), ('tender', 'Tender')],
                                  related='crm_lead_id.job_status')
    _work_order_prj = fields.Boolean(string='Work Order Project', default=False)
    esm_prjct = fields.Boolean(string="Esm Project", default=False)
    wrk_sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    project_boq_line = fields.One2many('project.boq.line', 'project_id', string="BOQ Lines")
    is_work_order_created = fields.Boolean(string="Is Work Order Created", default=False)
    is_adv_created = fields.Boolean(string="Is Advance Created", default=False)
    is_not_adv_created = fields.Boolean(string="Is not Advance Created", default=False)
    project_total_amount = fields.Float(string="Total Amount")
    project_total_amount_adv = fields.Float(string="Total Amount adv")
    project_assembly_line_ids = fields.One2many('assemble.qty', 'project_id', string="Assembly Lines")
    project_adv = fields.Float(string="Project Adv")
    adv_per = fields.Float(string="Adv Per")
    advance_recovery = fields.Boolean(string="Advance Recovery")
    last_invoice = fields.Many2one('account.move', string="Account Move")
    retention_amount = fields.Float(string="Retention Amount(%)")
    adv_recvry = fields.Float(string="Advance recovery(%)")
    retention_dates = fields.Date(string="Retention Date")
    currency_id = fields.Many2one("res.currency", string="Currency", default=lambda self: self.env.company.currency_id)

    estimation_amount = fields.Float(string="estimation Amount", related='wrk_sale_order_id.estimated_amount',
                                     store=True)
    quotation_amount = fields.Monetary(string="Quotation Amount", currency_field='currency_id',
                                       related='wrk_sale_order_id.amount_total', store=True)
    total_invoiced_amount = fields.Monetary(string="Total Invoiced Amount", currency_field='currency_id',
                                            compute="_compute_invoice_details", )
    total_invoiced_amount_with_tax = fields.Monetary(string="Total Invoiced Amount With Tax",
                                                     currency_field='currency_id',
                                                     compute="_compute_invoice_details")
    pending_invoice_amount = fields.Monetary(string="Due Invoice Amount", currency_field='currency_id',
                                             compute="_compute_invoice_pending", )
    location = fields.Char(string="Project Location")
    lpo_number = fields.Char(string="LPO Number")
    lpo_date = fields.Date(string="LPO Date")
    type_project = fields.Selection([('post_tender', 'Post Tender'), ('pre_tender', 'Pre Tender')],
                                    string="Project Type")

    @api.depends('total_invoiced_amount', 'user_id', 'name', 'total_invoiced_amount_with_tax')
    def _compute_invoice_details(self):
        for record in self:
            record.total_invoiced_amount = 0.0
            record.total_invoiced_amount_with_tax = 0.0
            invoices = self.env['account.move'].search(
                [('project_job_id', '=', record.id), ('move_type', '=', 'out_invoice'), ('state', '!=', 'cancel')])
            if invoices:
                record.total_invoiced_amount = sum(invoices.mapped('amount_untaxed_signed'))
                record.total_invoiced_amount_with_tax = sum(invoices.mapped('amount_total_signed'))

    @api.depends('total_invoiced_amount', 'user_id', 'pending_invoice_amount')
    def _compute_invoice_pending(self):
        for record in self:
            record.pending_invoice_amount = 0.0
            invoices = self.env['account.move'].search(
                [('project_job_id', '=', record.id), ('move_type', '=', 'out_invoice'), ('state', '!=', 'cancel')])
            if invoices:
                record.pending_invoice_amount = sum(invoices.mapped('amount_residual'))

    def unlink(self):
        if not self.env.user.has_group('arm_customization.group_delete_user'):
            raise UserError(_("You do not have the access to delete records !!"))
        else:
            return super(Project, self).unlink()

    def action_create_worker(self):
        for line in self.project_boq_line:
            sequence_est_task = self.env['ir.sequence'].next_by_code('project.task.work.order')
            wr_user = self.env['res.users'].search(
                [('groups_id', '=', self.env.ref('arm_customization.group_work_order_manager').id),
                 ('groups_id', '!=', self.env.ref('base.user_admin').id),
                 ('groups_id', 'not in', self.env.ref('base.group_system').id)])
            stage_id = self.env['project.task.type'].search([('stage_type', '=', 'shop_drawing')], limit=1)
            project_task = self.env['project.task'].sudo().create({
                'name': sequence_est_task,
                'job_wrk_name': 'Work order For -' + line.product_id.name,
                'sequence_code': sequence_est_task,
                'user_ids': [(6, 0, [user.id for user in wr_user])] if wr_user else False,
                'partner_id': self.partner_id.id,
                'project_id': self.id,
                '_is_work_task': True,
                'stage_wk': 'waiting',
                'stage_id': stage_id.id,
                'w_product': line.product_id.id,
                'p_qty': line.quantity,
                'p_uom': line.uom.id,
                'w_boq': line.id,
            })
            line.work_order = project_task.id
        self.sudo().is_work_order_created = True

    def create_adv_invoice(self):
        return {
            'name': 'Advance Invoice',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'advance.invoice.wizard',
            'target': 'new',
            'context': {
                'active_id': self.id,
                'default_project_total': self.project_total_amount,
            }
        }

    def create_invoice_prj(self):
        invoice = self.env['account.move'].search(
            [('project_job_id', '=', self.id), ('move_type', '=', 'out_invoice'), ('state', '=', 'draft')])
        if invoice:
            raise UserError(_("Already Pending Invoices Are There Please Post Or Cancel It !!"))
        val_list = []
        if self.project_boq_line:
            for rec in self.project_boq_line:
                if rec.balance_percentage > 0:
                    val_list.append((0, 0, {
                        'product_id': rec.product_id.id,
                        'boq_id': rec.id,
                        'quantity': rec.quantity,
                        'unit_price': rec.unit_price,
                        'subtotal': rec.subtotal,
                        'invoiced_percentage': rec.invoice_percentage,
                        'balance_percentage': rec.balance_percentage,
                        'uom': rec.uom.id,
                    }))
            verify_wizard = self.env['advance.invoice.wizard'].sudo().create({
                'project_id': self.id,
                'invoice_line_ids': val_list,
            })
            return {
                'name': 'Create Invoice',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                "view_type": "form",
                'res_model': 'advance.invoice.wizard',
                'res_id': verify_wizard.id,
                'target': 'new',
                'context': {
                    'active_id': self.id,
                }
            }

    def action_open_project_planning(self):
        return {
            'name': 'Project Planning',
            'view_type': 'list',
            'view_mode': 'list,form',
            'res_model': 'project.planning',
            'domain': [('project', '=', self.id)],
            'type': 'ir.actions.act_window',
        }

    def action_open_all_material_request(self):
        mr_ids = self.env['material.request.item'].sudo().search([('project_id', '=', self.id)])
        return {
            'name': 'Material Request',
            'view_type': 'list',
            'view_mode': 'list,form',
            'res_model': 'material.request.item',
            'domain': [('id', 'in', mr_ids.ids)],
            'type': 'ir.actions.act_window',
        }

    def action_open_all_po(self):
        po_ids = self.env['purchase.order'].sudo().search([('project', '=', self.id)])
        return {
            'name': 'Purchase Order',
            'view_type': 'list',
            'view_mode': 'list,form',
            'res_model': 'purchase.order',
            'domain': [('id', 'in', po_ids.ids)],
            'type': 'ir.actions.act_window',
        }

    def action_open_all_invoices(self):
        inv_ids = self.env['account.move'].sudo().search([('project_job_id', '=', self.id)])
        return {
            'name': 'Invoices',
            'view_type': 'list',
            'view_mode': 'list,form',
            'res_model': 'account.move',
            'domain': [('id', 'in', inv_ids.ids), ('move_type', '=', 'out_invoice')],
            'type': 'ir.actions.act_window',
        }

    def action_project_reminder_retention(self):
        for rec in self:
            today = fields.Date.today()
            if rec.retention_dates:
                if rec.retention_dates in [today, today - relativedelta(days=1), today - relativedelta(days=2)]:
                    if rec.last_invoice and rec.last_invoice.amount_residual > 0:
                        account_admin_group = self.env.ref('account.group_account_manager')
                        account_admins = self.env['res.users'].search([('groups_id', 'in', account_admin_group.id)])
                        if self.env.user.email:
                            for user in account_admins:
                                if user.email:
                                    subject = f"Retention Reminder of {rec.name} - {rec.job_name} "
                                    body = f"""
                                                <p>Dear {user.name},</p>
                                                <p>This is a reminder that the retention amount for project <strong>${rec.name}</strong> is due on <strong>${rec.retention_dates}</strong>.</p>
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

    def create_delivery_order_prj(self):
        return {
            'name': 'Delivery Creation',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'create.delivery.wizard',
            'target': 'new',
            'context': {
                'active_id': self.id,
                'default_project_id': self.id
            }
        }


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    stage_type = fields.Selection(
        [('shop_drawing', 'Shop Drawing'), ('design', "Design"), ('material', 'Material'), ('sample', 'Sample'),
         ('material_request', 'Material Request'), ('fabrication', 'Fabrication'), ('production', 'Production'),
         ('delivered', 'Delivered'), ('mir_approved', 'MIR Approved'), ('eraction', 'Eraction'), ('qa_qc', 'QA/Qc'),
         ('wir', 'WIR'), ('built_submission', 'Built Submission'), ('invoiced', 'Invoiced'),
         ('estimation', 'Estimation')], string="Stage Type")
