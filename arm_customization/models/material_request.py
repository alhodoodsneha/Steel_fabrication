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


class MaterialRequestLineItem(models.Model):
    _name = 'material.request.line.item'
    _description = 'Material Request Line'
    _rec_name = 'item_id'

    item_id = fields.Many2one('product.product', string='Item')
    description = fields.Text(sting='Description')
    quantity = fields.Float(string='Quantity')
    material_item_id = fields.Many2one('material.request.item', string="Item")
    project_id = fields.Many2one('project.project', string='Project', related='material_item_id.project_id')
    task_id = fields.Many2one('project.task', string='work order', related='material_item_id.task_id')
    state = fields.Selection(
        [('new', 'Waiting For Approval'),
         ('approved', 'Approved'),
         ('reject', 'Reject')], string='State', default='new', related='material_item_id.state')
    pm_approve_date = fields.Date(string="Approval Date", tracking=True,related='material_item_id.pm_approve_date')
    kg_linear = fields.Float(string="Kg/Linear Mtr")
    length = fields.Float(string="Length")
    width = fields.Float(string="Width")
    uom_id = fields.Many2one('uom.uom', string="Uom")
    spec = fields.Char(string="Spec")
    total_weight = fields.Float(string="Total Weight")
    def action_view_on_hand(self):
        self.ensure_one()
        if not self.item_id:
            raise UserError(_("No product is selected for this line item."))
        return {
            'name': _('On-Hand Stock'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'stock.quant',
            'views': [(self.env.ref('stock.view_stock_quant_tree_editable').id, 'tree')],
            'target': 'new',
            'domain': [('product_id', '=', self.item_id.id)],
            'context': {
                'search_default_group_by_location_id': 1,
                'search_default_internal_loc': 1,
                'search_default_on_hand': 1,
                'create': False,
                'delete': False,
                'edit': False
            },
        }


class MaterialRequestItem(models.Model):
    _name = 'material.request.item'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Material Request Item'
    _rec_name = 'sequence'

    sequence = fields.Char(string='Sequence', tracking=True)
    user_id = fields.Many2one('res.users', string='User', tracking=True)
    date = fields.Date(string='Date', default=fields.Date.today(), tracking=True)
    task_id = fields.Many2one('project.task', string='work order')
    project_id = fields.Many2one('project.project', string='Job', tracking=True, related='task_id.project_id')
    mrp_id = fields.Many2one('mrp.production', string="Mrp")
    project_manager = fields.Many2one('res.users', string='Project Manager', related='project_id.user_id',
                                      tracking=True)
    request_line_ids = fields.One2many('material.request.line.item', 'material_item_id',
                                       string="Material Request", tracking=True)
    state = fields.Selection(
        [('new', 'Waiting For Approval'),
         ('approved', 'Approved'),
         ('reject', 'Reject')], string='State', default='new', tracking=True)
    requisition_deadline = fields.Date(string='Requisition Deadline', tracking=True)
    requisition_reason = fields.Text(string='Requisition Reason', tracking=True)
    pm_approve_date = fields.Date(string="Approval Date", tracking=True)
    rejected_date = fields.Date(string='Reject Date', tracking=True)
    rejected_by = fields.Many2one('res.users', string='Reject By', tracking=True)
    approved_by = fields.Many2one('res.users', string='Approved By', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('sequence', _('New')) == _('New'):
                vals['sequence'] = self.env['ir.sequence'].next_by_code('material.requisition.task')
        return super().create(vals_list)

    def action_first_approve_request(self):
        self.state = 'approved'
        self.approved_by = self.env.user.id
        self.pm_approve_date = fields.Date.today()
        if not self.env.user.email:
            raise UserError(_("Please Configure Your Email"))
        if self.user_id.email:
            subject = f"Material Request {self.sequence} for {self.task_id.name} - {self.project_id.name} Approved"
            body = f"""
                     <p>Hello {self.user_id.name},</p>
                     <p>Material Request For Job {self.task_id.name} - {self.project_id.name} is fully approved on {self.pm_approve_date}.</p>
                     <p>Best Regards,</p>
                     <p>{self.approved_by.name}</p>
                     """
            mail_values_employee = {
                'subject': subject,
                'body_html': body,
                'email_from': self.approved_by.email,
                'email_to': self.user_id.email,
            }
            mail_employee = self.env['mail.mail'].sudo().create(mail_values_employee)
            mail_employee.send()

    def action_reject_request(self):
        self.state = 'reject'
        self.rejected_by = self.env.user.id
        self.rejected_date = fields.Date.today()
        if not self.env.user.email:
            raise UserError(_("Please Configure Your Email"))
        if self.user_id.email:
            subject = f"Material Request {self.sequence} Rejected BY {self.env.user.name} "
            body = f"""
                                       <p>Hello {self.user_id.name},</p>
                                       <p>Material Request For Job {self.task_id.name} - {self.project_id.name}is rejected by {self.env.user.name}.</p>
                                       <p>Best Regards,</p>
                                       <p>{self.env.user.name}</p>
                                       """
            mail_values_employee = {
                'subject': subject,
                'body_html': body,
                'email_from': self.env.user.email,
                'email_to': self.user_id.email,
            }
            mail_employee = self.env['mail.mail'].sudo().create(mail_values_employee)
            mail_employee.send()

    def action_create_rfq(self):
        return {
            'name': 'Create RFQ Request',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'material.rfq.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        }
        }

    def action_open_rfq_all(self):
        po_ids = self.env['purchase.order'].sudo().search([('material_request','=',self.id)])
        if po_ids:
            return {
                'name': 'Purchase Order',
                'view_type': 'list',
                'view_mode': 'list,form',
                'res_model': 'purchase.order',
                'domain': [('id', 'in', po_ids.ids)],
                'type': 'ir.actions.act_window',
            }