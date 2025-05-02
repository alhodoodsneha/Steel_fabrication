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

from odoo import fields, models, _
from odoo.exceptions import UserError


class CreateDeliveryWizard(models.TransientModel):
    _name = 'create.delivery.wizard'
    _description = "Delivery Creation"

    project_id = fields.Many2one('project.project', string="Project", readonly=True)
    task_ids = fields.Many2many('assemble.qty', string="Assembly",
                                domain="[('project_id','=',project_id),('production_status','=','done'),('item_status','!=','delivered')]")

    def action_create_delivery_wrk(self):
        delivery = self.env['project.delivery'].sudo().create({
            'project_id': self.project_id.id,
            'sale_order_id': self.project_id.wrk_sale_order_id.id,
            'delivery_line_ids': [(0, 0, {
                'assembly_id': line.id,
                'product_id': line.product_id.id,
                'task_id': line.work_id.id,
                'quantity': line.qty,
            }) for line in self.task_ids],
            'delivery_date': fields.Date.today(),
        })
        for rec in self.task_ids:
            rec.action_delivered()
