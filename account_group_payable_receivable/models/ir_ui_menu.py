# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    def _load_menus_blacklist(self):
        res = super()._load_menus_blacklist()
        if self.env.user.has_group('account_group_payable_receivable.group_account_receivable'):
            res.append(self.env.ref('account.menu_finance_entries').id)
            res.append(self.env.ref('account.menu_board_journal_1').id)
            res.append(self.env.ref('account.menu_finance_payables').id)
            res.append(self.env.ref('account.menu_finance_reports').id)
            res.append(self.env.ref('account.menu_finance_configuration').id)
        if self.env.user.has_group('account_group_payable_receivable.group_account_payable'):
            res.append(self.env.ref('account.menu_board_journal_1').id)
            res.append(self.env.ref('account.menu_finance_receivables').id)
            res.append(self.env.ref('account.menu_finance_entries').id)
            res.append(self.env.ref('account.menu_finance_reports').id)
            res.append(self.env.ref('account.menu_finance_configuration').id)
        return res
