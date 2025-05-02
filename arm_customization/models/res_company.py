from email.policy import default

from odoo import api, models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    inspection_team = fields.Boolean(string="Inspection",default=False)
