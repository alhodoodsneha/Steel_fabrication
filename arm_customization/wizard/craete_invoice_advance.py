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
#############################################################################

from odoo import fields, models, _, api
from odoo.exceptions import UserError


class CreateInvoiceLines(models.TransientModel):
    _name = 'advance.invoice.line.wizard'
    _description = "Invoice Lines"

    product_id = fields.Many2one('product.product', string="Product")
    boq_id = fields.Many2one('project.boq.line', string="Product")
    quantity = fields.Float(string="Qty")
    unit_price = fields.Float(string="Unit Price")
    uom = fields.Many2one('uom.uom', string="UOM")
    subtotal = fields.Float(string="Subtotal", store=True)
    invoiced_percentage = fields.Float(string="Invoiced Percentage")
    balance_percentage = fields.Float(string="Balance Percentage")
    to_invoice_percentage = fields.Float(string="To Invoice %")
    invoice_price = fields.Float(string="To Invoice Price", compute='_compute_invoice_price')
    wizard_id = fields.Many2one('advance.invoice.wizard', string="Wizard")

    @api.depends('subtotal', 'to_invoice_percentage')
    def _compute_invoice_price(self):
        for rec in self:
            if rec.to_invoice_percentage > 0 and rec.subtotal > 0:
                rec.invoice_price = (rec.subtotal * rec.to_invoice_percentage) / 100
            else:
                rec.invoice_price = 0.0

    @api.onchange('to_invoice_percentage')
    def _onchange_to_invoice_percentage(self):
        if self.to_invoice_percentage > self.balance_percentage:
            raise UserError(_("Invoice Percentage Must Be Less Than Balance Percentage!!"))


class CreateInvoiceAdvance(models.TransientModel):
    _name = 'advance.invoice.wizard'
    _description = "Advance Invoice"

    project_id = fields.Many2one('project.project', string="Project")
    invoice_line_ids = fields.One2many('advance.invoice.line.wizard', 'wizard_id', string="Invoice Line")

    def action_adv_create_adv(self):
        all_zero_balance = all(line.to_invoice_percentage > 0 for line in self.invoice_line_ids)
        if not all_zero_balance:
            raise UserError(_("All Lines Should Be Greater Than Zero!!"))
        project_id = self.project_id
        invoice_lines = []
        total_inv_pr = 0
        analytic_id = project_id.analytic_account_id.id
        for rec in self.invoice_line_ids:
            invoice_price = ((rec.subtotal * rec.to_invoice_percentage) / 100)
            total_inv_pr = total_inv_pr + invoice_price
            invoice_lines.append((0, 0, {
                'name': rec.boq_id.description,
                'quantity': 1,
                'price_unit': invoice_price,
                'boq_line': rec.boq_id.id,
                'product_id': rec.product_id.id,
                'product_uom_id': rec.uom.id,
                'analytic_distribution': {
                    analytic_id: 100.0,
                },
                'invoice_per': rec.to_invoice_percentage,
            }))
        if self.project_id.adv_recvry > 0.0:
            amount_rec = ((total_inv_pr * self.project_id.adv_recvry) / 100)
            advance_recovery_prd = self.env['product.template'].search([('advance_recovery', '=', True)], limit=1)
            if not advance_recovery_prd:
                raise UserError(_("Please Configure An Advance Recovery Product!!"))
            for product in advance_recovery_prd.product_variant_id:
                invoice_lines.append((0, 0, {
                    'name': 'Advance Recovery',
                    'quantity': 1,
                    'price_unit': -amount_rec,
                    'product_id': product.id,
                    'product_uom_id': product.uom_id.id,
                    'analytic_distribution': {
                        analytic_id: 100.0,
                    },
                    'invoice_per': 0.0,
                    'adv_line': True,
                }))
        if self.project_id.retention_amount > 0.0:
            amount_retention = ((total_inv_pr * self.project_id.retention_amount) / 100)
            retention_prd = self.env['product.template'].search([('retention', '=', True)], limit=1)
            if not retention_prd:
                raise UserError(_("Please Configure Retention Product!!"))
            for product in retention_prd.product_variant_id:
                invoice_lines.append((0, 0, {
                    'name': 'Retention',
                    'quantity': 1,
                    'price_unit': -amount_retention,
                    'product_id': product.id,
                    'product_uom_id': product.uom_id.id,
                    'analytic_distribution': {
                        analytic_id: 100.0,
                    },
                    'invoice_per': 0.0,
                    'retention_line': True,
                }))
        invoices = self.env['account.move'].search(
            [('project_job_id', '=', self.project_id.id), ('move_type', '=', 'out_invoice'),
             ('state', '=', 'posted')])
        if invoices:
            account_move = self.env['account.move'].sudo().create({
                'partner_id': project_id.partner_id.id,
                'move_type': 'out_invoice',
                'invoice_line_ids': invoice_lines,
                'sale_inv_id': project_id.wrk_sale_order_id.id,
                'project_job_id': project_id.id,
                'project_job': project_id.job_name,
                'lpo_no': project_id.lpo_number,
                'job_status': project_id.job_status,
                'job_no': project_id.name,
                'job_location': project_id.location,
                'previous_invoice_ids': invoices.ids,
            })
        else:
            account_move = self.env['account.move'].sudo().create({
                'partner_id': project_id.partner_id.id,
                'move_type': 'out_invoice',
                'invoice_line_ids': invoice_lines,
                'sale_inv_id': project_id.wrk_sale_order_id.id,
                'project_job_id': project_id.id,
                'project_job': project_id.job_name,
                'lpo_no': project_id.lpo_number,
                'job_status': project_id.job_status,
                'job_no': project_id.name,
                'job_location': project_id.location,
            })
        if project_id.job_status == 'job_in_hand':
            account_move.job_status = 'Job In Hand'
        elif project_id.job_status == 'tender':
            account_move.job_status = 'Tender'
