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

from odoo import api, models, fields, _
from odoo.exceptions import UserError
from odoo.tools.populate import compute


class MaterialRequisitionLineWizard(models.TransientModel):
    _name = 'material.wizard.line'
    _description = "Material Line"

    item_id = fields.Many2one('product.product', string='Product', domain=[('type', '=', 'product')])
    description = fields.Text(sting='Description')
    qty = fields.Float(string='Quantity')
    wizard_id = fields.Many2one('material.requisition.wizard', string='Wizard')
    kg_linear = fields.Float(string="Kg/Linear Mtr")
    length = fields.Float(string="Length")
    width = fields.Float(string="Width")
    uom_id = fields.Many2one('uom.uom', string="Uom")
    spec = fields.Char(string="Spec")
    total_weight = fields.Float(string="Total Weight", compute='_compute_total_weight')

    @api.depends('length', 'width', 'kg_linear', 'qty')
    def _compute_total_weight(self):
        for rec in self:
            rec.total_weight = 0.0
            if rec.length and rec.width and rec.kg_linear and rec.qty:
                rec.total_weight = (rec.length * rec.width * rec.kg_linear * rec.qty)


class MaterialRequisitionWizard(models.TransientModel):
    _name = 'material.requisition.wizard'
    _description = "Material Request"

    user_id = fields.Many2one('res.users', string='Requester', default=lambda self: self.env.user)
    date = fields.Date(string='Date', default=fields.Date.today())
    work_order = fields.Many2one('project.task', string="Work Order")
    mrp_id = fields.Many2one('mrp.production', string="Mrp")
    material_line_ids = fields.One2many('material.wizard.line', 'wizard_id', string='Lines')
    requisition_deadline = fields.Date(string='Requisition Deadline', tracking=True)

    def action_done_material_request(self):
        if self.material_line_ids:
            self.env['material.request.item'].create({
                'user_id': self.user_id.id,
                'task_id': self.work_order.id,
                'requisition_deadline': self.requisition_deadline,
                'mrp_id': self.mrp_id.id if self.mrp_id else False,
                'request_line_ids': [(0, 0, {
                    'item_id': line.item_id.id,
                    'description': line.description,
                    'quantity': line.qty,
                    'kg_linear': line.kg_linear,
                    'length': line.length,
                    'width': line.width,
                    'spec': line.spec,
                    'total_weight': line.total_weight,
                    'uom_id': line.uom_id.id,
                }) for line in self.material_line_ids],
            })
        else:
            raise UserError(_("Please add the materials"))


class RfqCreateWizard(models.TransientModel):
    _name = 'material.rfq.wizard'
    _description = "RFQ Create"

    supplier_id = fields.Many2one('res.partner', string="Supplier", domain=[('is_vendor', '=', True)])

    def action_create_rfq(self):
        material_id = self.env['material.request.item'].sudo().search([('id', '=', self.env.context['active_id'])])
        self.env['purchase.order'].sudo().create({
            'partner_id' :self.supplier_id.id,
            'material_request':material_id.id,
            'order_line': [(0, 0, {
                'product_id': line.item_id.id,
                'name': line.description,
                'product_qty': line.quantity,
                'product_uom': line.uom_id.id,
            }) for line in material_id.request_line_ids],

        })
