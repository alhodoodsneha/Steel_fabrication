from odoo import models, fields
from datetime import date


class DeferredEntryLine(models.Model):
    _name = 'deferred.entry.line'

    schedule_date = fields.Date(string="Date")
    deferred_account = fields.Many2one('deferred.entry.revenue', string="Deferred Account")
    account_move_id = fields.Many2one('account.move', string="Move", related='deferred_account.account_move_id')
    company_id = fields.Many2one(
        related='account_move_id.company_id', store=True, readonly=True, precompute=True,
        index=True,
    )
    company_currency_id = fields.Many2one(
        string='Company Currency',
        related='account_move_id.company_currency_id', readonly=True, store=True, precompute=True,
    )
    debit = fields.Monetary(
        string='Debit', store=True,
        currency_field='company_currency_id',
    )
    credit = fields.Monetary(
        string='Credit',
        store=True,
        currency_field='company_currency_id',
    )
    account_id = fields.Many2one('account.account', string="Account")
    _is_posted = fields.Boolean(string='Posted', default=False)
    partner_id = fields.Many2one('res.partner', string="Partner", related='deferred_account.partner_id')
    status = fields.Selection([('post', 'Posted'), ('draft', 'Draft')])
    is_debit = fields.Boolean(string='Debit', defaul=False)
    is_credit = fields.Boolean(string='Credit', defaul=False)
    is_corrected = fields.Boolean(string='Corrected', defaul=False)

class DeferredEntryRevenue(models.Model):
    _name = 'deferred.entry.revenue'
    _description = 'Deferred Revenue'
    _rec_name = 'account_move_id'

    amount = fields.Float(string="Amount")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    period = fields.Selection(
        [('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('6month', '6 Month'), ('yearly', 'Yearly')])
    journal_id = fields.Many2one('account.journal', string="Journal")
    credit_acc = fields.Many2one('account.account', string="Credit A/C")
    debit_acc = fields.Many2one('account.account', string="Debit A/C")
    account_move_id = fields.Many2one('account.move', string="Move")
    company_id = fields.Many2one(
        related='account_move_id.company_id', store=True, readonly=True, precompute=True,
        index=True,
    )
    company_currency_id = fields.Many2one(
        string='Company Currency',
        related='account_move_id.company_currency_id', readonly=True, store=True, precompute=True,
    )
    line_ids = fields.One2many('deferred.entry.line', 'deferred_account', string="Deferred Line")
    partner_id = fields.Many2one('res.partner', string="Partner")

    def create_journal_entry_for_today(self):
        today = date.today()
        lines = self.env['deferred.entry.line'].search([('schedule_date', '=', today), ('_is_posted', '=', False), ('is_credit', '=', True)])
        for line in lines:
            journal_entry_lines = [
                (0, 0, {
                    'debit': line.credit,
                    'credit': 0.0,
                    'account_id': line.deferred_account.debit_acc.id,
                    'partner_id': line.partner_id.id if line.partner_id else False,
                }),
                (0, 0, {
                    'debit': 0.0,
                    'credit': line.credit,
                    'account_id': line.deferred_account.credit_acc.id,
                    'partner_id': line.partner_id.id if line.partner_id else False,
                })
            ]

            journal_entry = self.env['account.move'].create({
                'journal_id': line.deferred_account.journal_id.id,
                'date': line.schedule_date,
                'line_ids': journal_entry_lines,
                'ref': f"Deferred Revenue Entry for {line.partner_id.name}" if line.partner_id else 'Deferred Revenue Entry',
                'move_type': 'entry',
                'state': 'draft',  # Adjust if needed, typically 'draft'
            })

            # Mark the line as posted
            line._is_posted = True
            line.status = 'post'
        corrected_lines = self.env['deferred.entry.line'].search(
            [('schedule_date', '=', today), ('_is_posted', '=', False), ('is_corrected', '=', True)])
        for corrected_line in corrected_lines:
            if corrected_line.is_credit:
                journal_entry_lines = [
                    (0, 0, {
                        'debit': corrected_lines.credit,
                        'credit': 0.0,
                        'account_id': line.deferred_account.debit_acc.id,
                        'partner_id': line.partner_id.id if line.partner_id else False,
                    }),
                    (0, 0, {
                        'debit': 0.0,
                        'credit': corrected_lines.credit,
                        'account_id': line.deferred_account.credit_acc.id,
                        'partner_id': line.partner_id.id if line.partner_id else False,
                    })
                ]

                journal_entry = self.env['account.move'].create({
                    'journal_id': line.deferred_account.journal_id.id,
                    'date': line.schedule_date,
                    'line_ids': journal_entry_lines,
                    'ref': f"Deferred Revenue Entry for {line.partner_id.name}" if line.partner_id else 'Deferred Revenue Entry Corrected',
                    'move_type': 'entry',
                    'state': 'draft',  # Adjust if needed, typically 'draft'
                })
            else:
                journal_entry_lines = [
                    (0, 0, {
                        'debit': corrected_lines.debit,
                        'credit': 0.0,
                        'account_id': line.deferred_account.credit_acc.id,
                        'partner_id': line.partner_id.id if line.partner_id else False,
                    }),
                    (0, 0, {
                        'debit': 0.0,
                        'credit': corrected_lines.debit,
                        'account_id': line.deferred_account.debit_acc.id,
                        'partner_id': line.partner_id.id if line.partner_id else False,
                    })
                ]

                journal_entry = self.env['account.move'].create({
                    'journal_id': line.deferred_account.journal_id.id,
                    'date': line.schedule_date,
                    'line_ids': journal_entry_lines,
                    'ref': f"Deferred Revenue Entry for {line.partner_id.name}" if line.partner_id else 'Deferred Revenue Entry Corrected',
                    'move_type': 'entry',
                    'state': 'draft',  # Adjust if needed, typically 'draft'
                })
            corrected_line._is_posted = True
