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
import base64
import xlrd


class BulkItemUploadTask(models.TransientModel):
    _name = 'bulk.item.upload.task'
    _description = "Bulk Item Upload"

    file = fields.Binary(string='Upload File', required=True)
    filename = fields.Char(string='Filename')

    def action_process_file(self):
        if not self.file:
            raise UserError(_("Please upload a file."))
        task_id = self.env['project.task'].sudo().search([('id', '=', self.env.context['active_id'])])
        file_data = base64.b64decode(self.file)
        workbook = xlrd.open_workbook(file_contents=file_data)
        sheet = workbook.sheet_by_index(0)
        task_id.boq_material_ids.unlink()
        count = 1
        for row_no in range(1, sheet.nrows):
            prod_sku = str(sheet.cell(row_no, 1).value).strip()
            descr = str(sheet.cell(row_no, 2).value).strip()
            uom = str(sheet.cell(row_no, 3).value).strip()
            qty = float(sheet.cell(row_no, 4).value)
            price = float(sheet.cell(row_no, 5).value)
            total_price = float(sheet.cell(row_no, 6).value)
            uom_id = self.env['uom.uom'].search([('name', '=', uom)])
            if not uom_id:
                raise UserError(_("UOM '%s' not found.") % uom)
            product_id = self.env['product.product'].search([('name', '=', prod_sku)])
            uom_id = self.env['uom.uom'].search([('name', '=', uom)])
            sequence = task_id.name + '-00' + str(count)
            if not product_id:
                product_id = self.env['product.product'].sudo().create({
                    'name':prod_sku,
                    'uom_id':uom_id.id,
                })
            self.env['boq.material'].create({
                'task_id':task_id.id,
                'sequence':sequence,
                'product_id': product_id.id,
                'uom': uom_id.id,
                'description':descr,
                'quantity':qty,
                'unit_price': price,
                'subtotal':total_price,
            })
            count = count +1
