from odoo import api, models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    material_request = fields.Many2one('material.request.item',string="Material Request")
    work_order_ids = fields.Many2one('project.task',string="Work Order",related="material_request.task_id")
    project = fields.Many2one('project.project',string="Project",related="material_request.project_id")
