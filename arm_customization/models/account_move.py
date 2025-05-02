from odoo import api, models, fields, _
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    inv_sl_line_id = fields.Many2one('sale.order.line', string="Sale Order Line", copy=False)
    invoice_per = fields.Float(string="Invoice Percentage", copy=False)
    project_id_inv = fields.Many2one('project.project', string="Project")
    adv_line = fields.Boolean(string="Adv Line", default=False)
    retention_line = fields.Boolean(string="Retention Line", default=False)
    boq_line = fields.Many2one('project.boq.line', string="Boq Line")


class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_inv_id = fields.Many2one('sale.order', string="Sale Order", copy=False)
    job_no = fields.Char(string="Job No", copy=False)
    job_status = fields.Char(string="Project Status", copy=False)
    job_location = fields.Char(string="Project Location", copy=False)
    lpo_no = fields.Char(string="LPO NO", copy=False)
    cont_ref = fields.Char(string="Cont Ref", copy=False)
    po_value = fields.Char(string="PO Value", copy=False)
    wrk_dn_period = fields.Char(string="Work Done Period", copy=False)
    pi_prepared_by = fields.Char(string="PI Prepared By", copy=False)
    project_job = fields.Char(string="Project", copy=False)
    project_job_id = fields.Many2one('project.project', string="Project", copy=False,
                                     domain=[('_work_order_prj', '=', True)])
    division_job = fields.Char(string="Division", copy=False)
    gross_wrk_credit_to_date = fields.Float(string="Gross Work certified to date", copy=False)
    gross_wrk_credit_previous = fields.Monetary(string="Gross Work certified Previous", copy=False,
                                                currency_field='company_currency_id',
                                                compute='_compute_gross_vat_per')
    less_advance_previous = fields.Monetary(string="Less Advance Previous", copy=False,
                                            currency_field='company_currency_id',
                                            compute='_compute_less_advance_recovery')
    less_retention_previous = fields.Monetary(string="Less retention Previous", copy=False,
                                              compute='_compute_less_retention', currency_field='company_currency_id')
    less_advance_to_date = fields.Float(string="Less Advance To date", copy=False)
    less_retention_to_date = fields.Float(string="Less retention To date", copy=False)
    less_advance_this_month = fields.Float(string="Less Advance This Month", copy=False)
    less_retention_this_month = fields.Float(string="Less retention This Month", copy=False)
    subtotal_to_date = fields.Float(string="Subtotal To date", copy=False)
    subtotal_previous = fields.Monetary(string="Subtotal Previous", copy=False, compute='_compute_subtotal_previous',
                                     currency_field='company_currency_id')
    vat_previous = fields.Monetary(string="Vat Previous", copy=False, compute='_compute_vat_previous',
                                currency_field='company_currency_id')
    vat_to_date = fields.Float(string="Vat To Date", copy=False)
    net_amount_due_date_to_date = fields.Float(string="Net Amount Due For Payment To date", copy=False)
    net_amount_due_date_previous = fields.Monetary(string="Net Amount Due For Payment Previous", copy=False,
                                                compute='_compute_net_amount_previous',
                                                currency_field='company_currency_id')
    prepared_by = fields.Many2one('res.users', string="Prepared By")
    Designation = fields.Char(string="Designation")
    is_adv = fields.Boolean(string="Adv Invoice", default=False)
    previous_invoice_ids = fields.Many2many('account.move', 'rel_acc_move', 'current_invoice_id', 'previous_invoice_id',
                                            string="Previous Invoices")

    @api.depends('previous_invoice_ids', 'gross_wrk_credit_previous')
    def _compute_gross_vat_per(self):
        for rec in self:
            if rec.previous_invoice_ids:
                rec.gross_wrk_credit_previous = sum(inv.amount_untaxed_signed for inv in rec.previous_invoice_ids)
            else:
                rec.gross_wrk_credit_previous = 0.0

    @api.depends('previous_invoice_ids', 'subtotal_previous')
    def _compute_subtotal_previous(self):
        for rec in self:
            if rec.previous_invoice_ids:
                rec.subtotal_previous = sum(inv.amount_untaxed_signed for inv in rec.previous_invoice_ids)
            else:
                rec.subtotal_previous = 0.0

    @api.depends('previous_invoice_ids', 'vat_previous')
    def _compute_vat_previous(self):
        for rec in self:
            if rec.previous_invoice_ids:
                rec.vat_previous = sum(inv.amount_tax_signed for inv in rec.previous_invoice_ids)
            else:
                rec.vat_previous = 0.0

    @api.depends('previous_invoice_ids', 'net_amount_due_date_previous')
    def _compute_net_amount_previous(self):
        for rec in self:
            if rec.previous_invoice_ids:
                rec.net_amount_due_date_previous = sum(inv.amount_total_signed for inv in rec.previous_invoice_ids)
            else:
                rec.net_amount_due_date_previous = 0.0

    @api.depends('previous_invoice_ids', 'less_advance_previous')
    def _compute_less_advance_recovery(self):
        for rec in self:
            if rec.previous_invoice_ids:
                if rec.project_job_id.adv_recvry > 0:
                    lines = self.env['account.move.line'].search(
                        [('move_id', 'in', rec.previous_invoice_ids.ids), ('adv_line', '=', True)])
                    if lines:
                        rec.less_advance_previous = sum(inv.price_unit for inv in lines)
                    else:
                        rec.less_advance_previous = 0.0
                else:
                    rec.less_advance_previous = 0.0
            else:
                rec.less_advance_previous = 0.0

    @api.depends('previous_invoice_ids', 'less_retention_previous')
    def _compute_less_retention(self):
        for rec in self:
            if rec.previous_invoice_ids:
                if rec.project_job_id.retention_amount > 0:
                    lines = self.env['account.move.line'].search(
                        [('move_id', 'in', rec.previous_invoice_ids.ids), ('retention_line', '=', True)])
                    if lines:
                        rec.less_retention_previous = sum(inv.price_unit for inv in lines)
                    else:
                        rec.less_retention_previous = 0.0
                else:
                    rec.less_retention_previous = 0.0
            else:
                rec.less_retention_previous = 0.0

    def action_post(self):
        for line in self.invoice_line_ids:
            if line.inv_sl_line_id:
                if line.invoice_per > line.inv_sl_line_id.balanced_percentage:
                    raise UserError(_("Invoice percentage greater than balance percentage!!"))
        for line in self.invoice_line_ids:
            if line.inv_sl_line_id:
                line.sudo().inv_sl_line_id.balanced_percentage = line.inv_sl_line_id.sudo().balanced_percentage - line.invoice_per
                line.inv_sl_line_id.sudo().invoiced_percentage = line.inv_sl_line_id.sudo().invoiced_percentage + line.invoice_per
            if line.inv_sl_line_id.order_id.type_sale == 'lump_sum':
                line.inv_sl_line_id.sudo().total_amount_invoiced = line.inv_sl_line_id.sudo().total_amount_invoiced + line.price_unit
            else:
                line.inv_sl_line_id.sudo().total_qty_invoiced = line.inv_sl_line_id.sudo().total_qty_invoiced + line.quantity
        return super(AccountMove, self).action_post()
