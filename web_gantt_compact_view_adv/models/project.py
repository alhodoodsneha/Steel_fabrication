from odoo import api, fields, models, _
from odoo.exceptions import UserError
 
class ProjectPlanning(models.Model):
    _inherit = "project.planning"

    task_type = fields.Selection([
        ('task', 'Task')
        ], string="Task Type", required=True, default='task')
    color = fields.Integer('Project color', default=4)
    task_link_ids = fields.One2many('project.planning.link', 'source_id', string="Task Links")
    task_priority = fields.Selection([
        ('normal', 'Normal'),
        ('low', 'Low'),        
        ('high', 'High')
    ], string='Priority', required=True, default='normal')
    progress = fields.Integer(tracking=True)

    @api.onchange('end_date')
    def onchange_gantt_stop_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.end_date = self.start_date


    @api.model
    def search_read_links(self, domain=None):
        datas = []
        tasks = self.env['project.planning'].search(domain)
        for task in tasks:
            if task.task_link_ids:                
                for link in task.task_link_ids:                    
                    link_vals = {
                        'id' : link.id,
                        'source' : task.id,
                        'target': link.target_id.id, 
                        'type': link.link_type,
                    }
                    datas.append(link_vals)
        return datas

class ProjectPlanningLink(models.Model):
    _name = "project.planning.link"
    _description = "Project Task Links"

    source_id = fields.Many2one('project.planning', string='Task')
    target_id = fields.Many2one('project.planning', string='Target Task', required=True)
    link_type = fields.Selection([
        ('0', "Finish to Start"), 
        ('1', "Start to Start"), 
        ('2', "Finish to Finish"),
        ('3', "Start to Finish")
        ], string="Link Type", required=True, default='1')