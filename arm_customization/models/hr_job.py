from odoo import api, models,fields


class HrJob(models.Model):
    _inherit = 'hr.job'

    hour_rate = fields.Float('Hour rate')

