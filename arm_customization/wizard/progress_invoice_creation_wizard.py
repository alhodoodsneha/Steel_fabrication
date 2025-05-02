from odoo import api, models, fields, _
from odoo.exceptions import UserError


class ProgressInvoiceLine(models.TransientModel):
    _name = 'progress.invoice.line'
    _description = "Progress Invoice Line"

    name = fields.Char(string="Name")
    qty = fields.Float(string="Qty")
    unit_price = fields.Float(string="Unit price")
    line_id = fields.Many2one('sale.order.line', string="Sale Order Line")
    balanced_percentage = fields.Float(string="Balanced Percentage", store=True)
    inv_total_amount = fields.Float(string="Total", store=True)
    inv_percentage = fields.Float(string="Invoice Percentage", store=True)
    total_amount_invoice = fields.Float(string="Invoice Amount", store=True)
    total_qty_invoice = fields.Float(string="Invoiced qty", store=True)
    wizard_id = fields.Many2one('progress.invoice.creation', string="Progressive Wizard")
    type_sale = fields.Selection([('lump_sum', 'Lump sum'), ('qty', 'Qty')], string="Type", required=True,
                                 related='wizard_id.type_sale')


class ProgressInvoiceCreation(models.TransientModel):
    _name = 'progress.invoice.creation'
    _description = "Progress Invoice"

    invoice_percentage = fields.Float(string='Invoice Percentage')
    sale_order = fields.Many2one('sale.order', string="Sale Order")
    wizard_line_ids = fields.One2many('progress.invoice.line', 'wizard_id', string="Lines")
    type_sale = fields.Selection([('lump_sum', 'Lump sum'), ('qty', 'Qty')], string="Type", required=True,
                                 related='sale_order.type_sale')

    def action_apply_invoice(self):
        for line in self.wizard_line_ids:
            line.inv_percentage = self.invoice_percentage
            if self.type_sale == 'lump_sum':
                line.total_amount_invoice = (self.invoice_percentage / 100) * line.inv_total_amount
            else:
                line.total_qty_invoice = (self.invoice_percentage / 100) * line.qty
        return {
            'type': 'ir.actions.act_window',
            'name': 'Progress Invoice',
            'view_mode': 'form',
            'res_model': 'progress.invoice.creation',
            'res_id': self.id,
            'target': 'new',
        }

    def action_done_creation(self):
        exceeded_lines = []
        order_lines = []
        not_invoice = self.wizard_line_ids.filtered(lambda line: line.inv_percentage == 0.0)
        if not_invoice:
            raise UserError(_("Please Add Invoice percentage!!"))
        for line in self.wizard_line_ids:
            if line.inv_percentage > line.balanced_percentage:
                exceeded_lines.append(line.name)
            else:
                if self.type_sale == 'lump_sum':
                    total_per = line.balanced_percentage + line.inv_percentage
                    line.total_amount_invoice = (line.inv_percentage / 100) * line.inv_total_amount
                    if total_per == 100:
                        amount = line.line_id.total_amount_invoiced + line.total_amount_invoice
                        if amount != line.inv_total_amount:
                            line.total_amount_invoice = line.inv_total_amount - line.line_id.total_amount_invoiced
                    order_lines.append((0, 0, {
                        'name': line.name,
                        'quantity': 1,
                        'price_unit': line.total_amount_invoice,
                        'inv_sl_line_id': line.line_id.id,
                        'invoice_per': line.inv_percentage,
                    }))
                else:
                    total_per = line.balanced_percentage + line.inv_percentage
                    line.total_qty_invoice = (line.inv_percentage / 100) * line.qty
                    if total_per == 100:
                        qty_added = line.line_id.total_qty_invoiced + line.total_qty_invoice
                        if qty_added != line.qty:
                            line.total_qty_invoice = line.qty - line.line_id.total_qty_invoiced
                    order_lines.append((0, 0, {
                        'quantity': line.total_qty_invoice,
                        'price_unit': line.unit_price,
                        'name': line.name,
                        'inv_sl_line_id': line.line_id.id,
                        'invoice_per': line.inv_percentage,
                    }))
        if exceeded_lines:
            raise UserError(_(
                "The following lines have an Invoice Percentage greater than the Balance Percentage:\n%s"
            ) % "\n".join(exceeded_lines))
        self.env['account.move'].sudo().create({
            'partner_id': self.sale_order.partner_id.id,
            'move_type': 'out_invoice',
            'invoice_line_ids':order_lines,
            'sale_inv_id':self.sale_order.id,
        })

