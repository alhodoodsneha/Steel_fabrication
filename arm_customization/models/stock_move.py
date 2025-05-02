from odoo import api, models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'


    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")
    task_id = fields.Many2one('project.task',string="Task")