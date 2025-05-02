from odoo import api, models,fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'


    @api.model
    def create(self, vals):
        vals['barcode'] = self.env['ir.sequence'].next_by_code('emp.badge.sequence')
        return super(HrEmployee, self).create(vals)

    def action_update_badge(self):
        employee = self.env['hr.employee'].search([])
        if employee:
            for rec in employee:
                sequence = self.env['ir.sequence'].next_by_code('emp.badge.sequence')
                rec.barcode = sequence
