from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    bank = fields.Char(string='Bank')
    branch_bank = fields.Char(string='Branch')
    iban = fields.Char(string='IBAN')
    swift = fields.Char(string='Swift')
    trn = fields.Char(string='TRN')
    acc_no = fields.Char(string='Account Number')
    beneficiary_name = fields.Char(string="Beneficiary Name")
