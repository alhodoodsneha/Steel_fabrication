from odoo.exceptions import UserError
from odoo import api, models, fields, _


class BOQMaterial(models.Model):
    _name = 'boq.material'
    _description = 'BOQ Material'
    _rec_name = 'sequence'

    sequence = fields.Char(string="Serial Number", copy=False)
    product_id = fields.Many2one('product.product', string="Product", required=True)
    description = fields.Char(string="Description")
    quantity = fields.Float(string="Qty")
    uom = fields.Many2one('uom.uom', string="UOM")
    unit_price = fields.Float(string="Unit Price")
    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal")
    task_id = fields.Many2one('project.task', string="Task")
    project_id = fields.Many2one('project.project', string="Project", related='task_id.project_id', store=True)


    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.quantity * record.unit_price


class AssembleQty(models.Model):
    _name = 'assemble.qty'
    _description = 'Assemble Qty'
    _rec_name = 'assemble_mark'

    name = fields.Char(string="Name")
    assemble_mark = fields.Char(string="Assemble Mark")
    profile = fields.Char(string="Profile")
    net_for_one = fields.Float(string="Net Area for one")
    net_for_all = fields.Float(string="Net Area for all")
    net_weight_for_one = fields.Float(string="Net Weight for one")
    net_weight_for_all = fields.Float(string="Net Weight for all")
    product_id = fields.Many2one('product.product', string="Product")
    qty = fields.Float(string="No")
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approve'), ('refuse', 'Refuse')], string="State",
                             default='draft')
    comments = fields.Text(string="Comment")
    work_id = fields.Many2one('project.task', string="Task")
    stage = fields.Selection(
        [('waiting', 'Engineering'), ('qa_ist', 'QA/QC'), ('production', 'Production'), ('qa_qc', 'QA/QC'),
         ('delivered', 'Delivered'),
         ('invoiced', 'Invoiced')], string="Stage Work", related='work_id.stage_wk')
    related_mrp = fields.Many2one('mrp.production', string="Mrp")
    production_status = fields.Selection([('draft', 'Draft'),
                                          ('confirmed', 'Confirmed'),
                                          ('progress', 'In Progress'),
                                          ('to_close', 'To Close'),
                                          ('done', 'Done'),
                                          ('cancel', 'Cancelled')], string="Production Status",
                                         related='related_mrp.state')
    item_status = fields.Selection([('not_delivered', 'Not Delivered'), ('delivered', 'Delivered')],
                                   string="Item Status", defauit='not_delivered')
    stage_type = fields.Selection(
        [('shop_drawing', 'Shop Drawing'), ('design', "Design"), ('material', 'Material'), ('sample', 'Sample'),
         ('material_request', 'Material Request'), ('fabrication', 'Fabrication'), ('production', 'Production'),
         ('delivered', 'Delivered'), ('mir_approved', 'MIR Approved'), ('eraction', 'Eraction'), ('qa_qc', 'QA/Qc'),
         ('wir', 'WIR'), ('built_submission', 'Built Submission'), ('invoiced', 'Invoiced'),
         ('estimation', 'Estimation')], string="Stage Type",
        related='work_id.stage_type')
    created = fields.Boolean(string="Created", default=False)
    project_id = fields.Many2one('project.project',string="Project",related="work_id.project_id")
    partner_id = fields.Many2one('res.partner',string="Partner",related="work_id.partner_id")
    invoice_percentage = fields.Float(string="Invoice Percentage",compute='_compute_invoice_per')
    invoice_status = fields.Selection([('invoiced','Invoiced'),('to_invoice','to_invoice')],string="Invoice Status",default="to_invoice")

    def _compute_invoice_per(self):
        for rec in self:
            rec.invoice_percentage = 0.0
            if rec.work_id.assemble_line_ids:
                count = len(rec.work_id.assemble_line_ids.ids)
                per = 100 / count
                rec.invoice_percentage = per

    def action_approve(self):
        related_mrp = self.env['mrp.production'].sudo().create({
            'product_id': self.product_id.id,
            'product_qty': self.qty,
            'product_uom_id': self.product_id.uom_id.id,
            'work_order_id': self.work_id.id,
            'assemble_id': self.id,
        })
        self.related_mrp = related_mrp.id
        self.created = True

    def action_delivered(self):
        if self.production_status != 'done':
            raise UserError(_("Item can be delivered only after production."))
        move_line = self.env['stock.move.line'].sudo().search(
            [('product_id', '=', self.product_id.id), '|',
             ('move_id.raw_material_production_id', '=', self.related_mrp.id),
             ('move_id.production_id', '=', self.related_mrp.id)])
        if move_line:
            location_to = self.env['stock.location'].sudo().search([('usage','=','customer')],limit=1)
            location_from = move_line.location_dest_id
            picking_type = self.env['stock.picking.type'].search([
                ('code', '=', 'internal'),
                ('warehouse_id', '=', location_from.warehouse_id.id)
            ], limit=1)
            picking = self.env['stock.picking'].sudo().create({
                'picking_type_id': picking_type.id,
                'location_id': location_from.id,
                'location_dest_id': location_to.id,
                'partner_id': self.work_id.project_id.partner_id.id,
                'scheduled_date': fields.date.today(),
                'origin':self.work_id.project_id.wrk_sale_order_id.name,
            })
            stock_move_obj = self.env['stock.move']
            move_vals = {
                'name': self.product_id.display_name,
                'product_id': self.product_id.id,
                'product_uom_qty': self.qty,
                'product_uom': self.product_id.uom_id.id,
                'location_id': location_from.id,
                'location_dest_id': location_to.id,
                'picking_id': picking.id,
            }
            stock_move_obj.create(move_vals)
            picking.action_confirm()
            picking.action_assign()
            picking.button_validate()
        self.item_status = 'delivered'
