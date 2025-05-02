from odoo import api, models, fields, _


class ShopDrawingLIne(models.Model):
    _name = 'shop.drawing.line'
    _description = 'Shop Drawing'
    _rec_name = 'command_date'

    submitted_date = fields.Date(string="Submitted Date")
    command_date = fields.Date(string="Command Date")
    comments = fields.Text(string="Comments")
    task_id = fields.Many2one('project.task', string="Task")
    type = fields.Selection([('approve', 'Approve'), ('revision', 'Revision')], string="Type")
    revision = fields.Char(string="Revision")
    revision_shop_drawing_count = fields.Integer(string="Revision count")


class DesignLIne(models.Model):
    _name = 'design.line'
    _description = 'Design'
    _rec_name = 'command_date'

    submitted_date = fields.Date(string="Submitted Date")
    command_date = fields.Date(string="Command Date")
    comments = fields.Text(string="Comments")
    task_id = fields.Many2one('project.task', string="Task")
    type = fields.Selection([('approve', 'Approve'), ('revision', 'Revision')], string="Type")
    revision = fields.Char(string="Revision")
    revision_shop_drawing_count = fields.Integer(string="Revision count")


class MaterialSubmissionLIne(models.Model):
    _name = 'material.submission.line'
    _description = 'Material Submission'
    _rec_name = 'command_date'

    submitted_date = fields.Date(string="Submitted Date")
    command_date = fields.Date(string="Command Date")
    comments = fields.Text(string="Comments")
    task_id = fields.Many2one('project.task', string="Task")
    type = fields.Selection([('approve', 'Approve'), ('revision', 'Revision')], string="Type")
    revision = fields.Char(string="Revision")
    revision_shop_drawing_count = fields.Integer(string="Revision count")


class SampleSubmissionLIne(models.Model):
    _name = 'sample.submission.line'
    _description = 'Sample Submission'
    _rec_name = 'command_date'

    submitted_date = fields.Date(string="Submitted Date")
    command_date = fields.Date(string="Command Date")
    comments = fields.Text(string="Comments")
    task_id = fields.Many2one('project.task', string="Task")
    type = fields.Selection([('approve', 'Approve'), ('revision', 'Revision')], string="Type")
    revision = fields.Char(string="Revision")
    revision_shop_drawing_count = fields.Integer(string="Revision count")




class QAQcFail(models.Model):
    _name = 'qa.qc.status.line'
    _description = 'QA/QC Status'
    _rec_name = 'submitted_date'

    submitted_date = fields.Date(string="Submitted Date", default=fields.date.today())
    fail_type = fields.Selection([('fabrication_issue', 'Fabrication Issue'), ('operation_issue', 'Operation Issue'),
                                  ('engineering_issue', 'Engineering Issue')], string="Issue")
    reason = fields.Text(string="Reason")
    task_id = fields.Many2one('project.task',string="Task")
    user_id = fields.Many2one('res.users', string="User")



class WIRFail(models.Model):
    _name = 'wir.status.line'
    _description = 'WIR Status'
    _rec_name = 'submitted_date'

    submitted_date = fields.Date(string="Submitted Date", default=fields.date.today())
    fail_type = fields.Selection([('fabrication_issue', 'Fabrication Issue'), ('operation_issue', 'Operation Issue'),
                                  ('engineering_issue', 'Engineering Issue')], string="Issue")
    reason = fields.Text(string="Reason")
    task_id = fields.Many2one('project.task',string="Task")
    user_id = fields.Many2one('res.users', string="User")