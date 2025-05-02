from odoo import models,fields, api


class SalesApproveConfiguration(models.Model):
    _name = 'sale.approve.configuration'
    _description = 'Sales Verification'
    _rec_name = 'name'

    name = fields.Char(string="Name")
