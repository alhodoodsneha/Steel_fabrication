from odoo import api, models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    estimation_ok = fields.Boolean('Estimation Product', default=False)
    advance_recovery = fields.Boolean('Advance Recovery', default=False)
    retention = fields.Boolean('Retention', default=False)

