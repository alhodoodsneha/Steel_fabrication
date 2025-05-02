# -*- coding: utf-8 -*-
from odoo import fields, models


class IrAttachment(models.Model):
    """This class inherits from 'ir.attachment' and introduces two many-to-many
     relationships: 'doc_attach_rel' for associating HR employee documents and
    'attach_rel' for attaching general HR documents to a record."""
    _inherit = 'ir.attachment'

    doc_attach_rel = fields.Many2many('hr.employee.document',
                                      'doc_attachment_ids',
                                      'attach_id3', 'doc_id',
                                      string="Attachment", invisible=1,
                                      help='This field allows you to associate'
                                           'HR employee documents with the '
                                           'record.')
    attach_rel = fields.Many2many('hr.document',
                                  'attach_ids', 'attachment_id3',
                                  'document_id',
                                  string="Attachment", invisible=1,
                                  help='This field allows you to attach HR '
                                       'documents to the record.')
