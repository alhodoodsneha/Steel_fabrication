from odoo import fields, models, api, _

class ProjectDelivery(models.Model):
    _name = 'project.delivery'
    _description = "Project Delivery"
    _rec_name = "code"

    code = fields.Char(string="Delivery Reference", copy=False, readonly=True)
    project_id = fields.Many2one('project.project', string="Project", required=True)
    sale_order_id = fields.Many2one('sale.order', string="Sale Order", required=True)
    partner_id = fields.Many2one('res.partner', string="Customer", related="sale_order_id.partner_id", store=True)
    delivery_line_ids = fields.One2many('project.delivery.line', 'delivery_id', string="Delivery Lines")
    delivery_date = fields.Date(string="Delivery date")
    dispatch_doc_no = fields.Char(string="Dispatch Document No")
    dispatch_through = fields.Char(string="Dispatch Through")
    destination = fields.Char(string="Destination")
    delivery_mode = fields.Char(string="Delivery Mode")
    terms_of_delivery = fields.Text(string="Terms of Delivery")
    container_no_seal_no = fields.Char(string="Container No and Seal No")
    vehicle_no = fields.Char(string="Vehicle No")
    drivers_name = fields.Char(string="Driver Name")
    drivers_mobile = fields.Char(string="Driver Mobile")
    port_of_loading = fields.Char(string="Port Of Loading")
    company_id = fields.Many2one('res.company', string="company",default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string="User",default=lambda self: self.env.user)
    location = fields.Char(string="Project Location",related='project_id.location')
    lpo_number = fields.Char(string="LPO Number",related='project_id.lpo_number')
    lpo_date = fields.Date(string="LPO Date",related='project_id.lpo_date')

    @api.model
    def create(self, vals):
        res = super(ProjectDelivery, self).create(vals)
        res.code = self.env['ir.sequence'].next_by_code('project.delivery')
        return res



class ProjectDeliveryLine(models.Model):
    _name = 'project.delivery.line'
    _description = "Project Delivery Line"

    delivery_id = fields.Many2one('project.delivery', string="Delivery")
    assembly_id = fields.Many2one('assemble.qty', string="Assembly", required=True)
    task_id = fields.Many2one('project.task', string="Work Order", required=True)
    product_id = fields.Many2one('product.product', string="Product", required=True)
    quantity = fields.Float(string="Quantity", required=True)
