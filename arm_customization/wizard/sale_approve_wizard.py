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

class SaleApproveLine(models.TransientModel):
    _name = 'sale.approve.wizard.line'
    _description = 'Sales Approve Line'

    name = fields.Char(string="Item Name")
    is_verified = fields.Boolean(string="Verified", default=False)
    configuration_id = fields.Many2one(
        'sale.approve.wizard', string="Configuration"
    )
    stage = fields.Selection([('done', 'Done')])

    def action_verify(self):
        self.is_verified = True
        self.stage = 'done'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.approve.wizard',
            'view_mode': 'form',
            'res_id': self.configuration_id.id,
            'target': 'new',
        }


class SaleApproveWizard(models.TransientModel):
    _name = 'sale.approve.wizard'
    _description = 'Verify Items'

    sale_order_id = fields.Many2one('sale.order',string="Sale Order")
    verification_line_ids = fields.One2many('sale.approve.wizard.line', 'configuration_id',
                                            string="Verification Lines")

    def action_done_process(self):
        all_done = all(line.is_verified for line in self.verification_line_ids)
        if not all_done:
            raise UserError(_("Please Do all the precautions !!"))
        self.sale_order_id.sudo().estimated_task.sudo().state = '1_done'
        for line in self.verification_line_ids:
            self.env['sale.verified.line'].create({
                'name':line.name,
                'user_id':self.env.user.id,
                'stage':'done',
                'sale_id':self.sale_order_id.id,
            })
        self.sale_order_id.sudo().estimated_task.sudo().crm_lead_id.sudo().quotation_type = 'approved'
        self.sale_order_id.action_confirm()

