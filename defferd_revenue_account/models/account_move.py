from odoo import models, fields, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_create_deferral = fields.Boolean(string="Deferral Created", default=False)

    def action_create_deferral(self):
        debit_lines = self.line_ids.filtered(lambda line: line.debit > 0)[:1]
        if not debit_lines:
            raise UserError(_('Debit Line Not Found'))
        self.is_create_deferral = True
        return {
            'name': 'Deferral Revenue',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'deferred.revenue.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        'default_start_date': self.date,
                        'default_amount': debit_lines.debit if debit_lines else False,
                        'default_journal_id': self.journal_id.id,
                        'default_account_move_id': self.id,
                        'default_credit_acc': debit_lines.account_id.id if debit_lines else False,
                        'default_partner_id': debit_lines.partner_id.id if debit_lines and debit_lines.partner_id else False,
                        }
        }
