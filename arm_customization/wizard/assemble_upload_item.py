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


class AssembleItemUpload(models.TransientModel):
    _name = 'assemble.item.upload'
    _description = "Assemble Item Upload"

    file = fields.Binary(string='Upload File', required=True)
    filename = fields.Char(string='Filename')

    def action_process_file(self):
        if not self.file:
            raise UserError(_("Please upload a file."))
        task = self.env['project.task'].sudo().search([('id', '=', self.env.context['active_id'])])
        file_data = base64.b64decode(self.file)
        workbook = xlrd.open_workbook(file_contents=file_data)
        sheet = workbook.sheet_by_index(0)
        task.assemble_line_ids.unlink()
        count = 0
        for row_no in range(1, sheet.nrows):
            assemble_mark = str(sheet.cell(row_no, 0).value).strip()
            qty = float(sheet.cell(row_no, 1).value)
            name = str(sheet.cell(row_no, 2).value).strip()
            profile = str(sheet.cell(row_no, 3).value).strip()
            net_for_one = float(sheet.cell(row_no, 4).value)
            net_for_all = float(sheet.cell(row_no, 5).value)
            net_weight_for_one = float(sheet.cell(row_no, 6).value)
            net_weight_for_all = float(sheet.cell(row_no, 7).value)
            product_id = self.env['product.product'].create({
                'name':assemble_mark + '00'+ str(count) ,
                'type': 'product',
            })
            count = count +1
            self.env['assemble.qty'].create({
                'assemble_mark':assemble_mark,
                'name':name,
                'profile':profile,
                'net_for_one':net_for_one,
                'net_for_all':net_for_all,
                'net_weight_for_one':net_weight_for_one,
                'net_weight_for_all':net_weight_for_all,
                'work_id': task.id,
                'qty':qty,
                'product_id':product_id.id,
            })
