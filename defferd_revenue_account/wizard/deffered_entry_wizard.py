from odoo import models, fields
from dateutil.relativedelta import relativedelta


class DeferredRevenueWizard(models.TransientModel):
    _name = 'deferred.revenue.wizard'
    _description = "Deferred Revenue Wizard"

    amount = fields.Float(string="Amount")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    period = fields.Selection(
        [('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('6month', '6 Month'), ('yearly', 'Yearly')])
    journal_id = fields.Many2one('account.journal', string="Journal")
    credit_acc = fields.Many2one('account.account', string="Credit A/C")
    debit_acc = fields.Many2one('account.account', string="Debit A/C")
    account_move_id = fields.Many2one('account.move', string="Move")
    partner_id = fields.Many2one('res.partner', string="Partner")

    def action_create_deferred(self):
        schedule_dates = self._generate_schedule_dates()
        deferred_revenue = self.env['deferred.entry.revenue'].create({
            'amount': self.amount,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'period': self.period,
            'journal_id': self.journal_id.id,
            'credit_acc': self.credit_acc.id,
            'debit_acc': self.debit_acc.id,
            'account_move_id': self.account_move_id.id,
            'partner_id': self.partner_id.id if self.partner_id else False,
        })
        self.env['deferred.entry.line'].create({
            'schedule_date': self.start_date,
            'deferred_account': deferred_revenue.id,
            'debit': self.amount,  # Divide amount equally over the schedule
            'credit': 0.0,
            'is_debit': True,
            'is_credit': False,
            'account_move_id': self.account_move_id.id,
            'account_id': self.credit_acc.id,  # Use debit account for the lines
            'partner_id': self.account_move_id.partner_id.id if self.partner_id else False,  # Related partner
        })
        for schedule_date in schedule_dates:
            self.env['deferred.entry.line'].create({
                'schedule_date': schedule_date,
                'deferred_account': deferred_revenue.id,
                'debit': 0.0,  # Divide amount equally over the schedule
                'is_debit': False,
                'is_credit': True,
                'credit': self.amount / len(schedule_dates),
                'account_move_id': self.account_move_id.id,
                'account_id': self.credit_acc.id,  # Use debit account for the lines
                'partner_id': self.account_move_id.partner_id.id,  # Related partner
            })
        deferred_line = self.env['deferred.entry.line'].search(
            [('deferred_account', '=', deferred_revenue.id), ('is_credit', '=', True),
             ('schedule_date', '=', fields.Date.today())], limit=1)
        journal_entry_lines = []
        if deferred_line:
            journal_entry_lines = [
                (0, 0, {
                    'debit': deferred_line.credit,
                    'credit': 0.0,
                    'account_id': self.debit_acc.id,  # Debit from the debit account
                    'partner_id': deferred_line.partner_id.id if deferred_line.partner_id else False,
                }),
                (0, 0, {
                    'debit': 0.0,
                    'credit': deferred_line.credit,
                    'account_id': self.credit_acc.id,  # Credit to the credit account
                    'partner_id': deferred_line.partner_id.id if deferred_line.partner_id else False,
                }),
            ]
            journal_entry = self.env['account.move'].create({
                'journal_id': deferred_line.deferred_account.journal_id.id,
                'date': deferred_line.schedule_date,  # You can choose the appropriate date
                'line_ids': journal_entry_lines,
                'ref': 'Deferred Revenue for {}'.format(self.partner_id.name if self.partner_id else 'General'),
                'state': 'draft',
                'move_type': 'entry'
            })
            total_debit = sum(self.env['deferred.entry.line'].search([
                ('deferred_account', '=', deferred_revenue.id),
                ('is_debit', '=', True)
            ]).mapped('debit'))

            total_credit = sum(self.env['deferred.entry.line'].search([
                ('deferred_account', '=', deferred_revenue.id),
                ('is_credit', '=', True)
            ]).mapped('credit'))

            # Check for any difference between debit and credit
            if total_debit != total_credit:
                difference = total_debit - total_credit
                if total_debit > total_credit:
                    self.env['deferred.entry.line'].create({
                        'schedule_date': schedule_date,
                        'deferred_account': deferred_revenue.id,
                        'debit': 0.0,  # Divide amount equally over the schedule
                        'is_debit': False,
                        'is_credit': True,
                        'is_corrected': True,
                        'credit': difference,
                        'account_move_id': self.account_move_id.id,
                        'account_id': self.credit_acc.id,  # Use debit account for the lines
                        'partner_id': self.account_move_id.partner_id.id,  # Related partner
                    })
                else:
                    self.env['deferred.entry.line'].create({
                        'schedule_date': schedule_date,
                        'deferred_account': deferred_revenue.id,
                        'debit': difference,  # Divide amount equally over the schedule
                        'is_debit': True,
                        'is_credit': False,
                        'is_corrected': True,
                        'credit': 0.0,
                        'account_move_id': self.account_move_id.id,
                        'account_id': self.credit_acc.id,  # Use debit account for the lines
                        'partner_id': self.account_move_id.partner_id.id,  # Related partner
                    })
            deferred_line._is_posted = True
            deferred_line.status = 'post'
        return {
            'type': 'ir.actions.act_window_close'
        }

    def _generate_schedule_dates(self):
        """Generate a list of dates based on the period (monthly, quarterly, etc.)"""
        schedule_dates = []
        current_date = self.start_date
        if self.period == 'monthly':
            delta = relativedelta(months=1)
        elif self.period == 'quarterly':
            delta = relativedelta(months=3)
        elif self.period == '6month':
            delta = relativedelta(months=6)
        elif self.period == 'yearly':
            delta = relativedelta(years=1)
        else:
            delta = None

        while current_date <= self.end_date:
            schedule_dates.append(current_date)
            current_date += delta

        return schedule_dates
