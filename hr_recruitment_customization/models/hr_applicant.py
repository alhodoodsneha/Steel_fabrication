# -*- coding: utf-8 -*-
#############################################################################

#    Alhodood Technologies.
#
#    Copyright (C) 2024-TODAY Alhodood Technologies(<https://www.alhodood.com>)
#    Author: Alhodood Technologies(<https://www.alhodood.com>)
#
#    You can modify it under the terms of the GNU Affero General Public License (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License (AGPL v3) for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import fields, models, api,_
from datetime import datetime
from markupsafe import Markup
from num2words import num2words


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    other_allowance_emp = fields.Float(string="Other Allowance")
    emp_country_id = fields.Many2one('res.country', string="Country")
    emp_state_id = fields.Many2one('res.country.state', string="State", domain="[('country_id', '=', emp_country_id)]")
    selection_status = fields.Selection([
        ('accepted', 'Offer Accepted'),
        ('rejected', 'Offer Rejected')
    ], string="Selection Status", readonly=True)
    sequence = fields.Char(string='Sequence', copy=False, readonly=True,
                           default=lambda self: _('New'), tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('sequence', _('New')) == _('New'):
                vals['sequence'] = self.env['ir.sequence'].next_by_code('employee.offer.letter')
        return super().create(vals_list)

    def get_ordinal_date(self):
        """Returns the current day with the ordinal suffix as superscript."""
        today = fields.Date.context_today(self)  # Get current date
        day = today.day

        if 11 <= day <= 13:
            suffix = "th"
        elif day % 10 == 1:
            suffix = "st"
        elif day % 10 == 2:
            suffix = "nd"
        elif day % 10 == 3:
            suffix = "rd"
        else:
            suffix = "th"
        formatted_date = today.strftime(f"{day}<sup>{suffix}</sup> %B %Y")
        return Markup(formatted_date)

    def amount_to_words(self, amount):
        amount_words = num2words(amount, lang='en').capitalize()
        return amount_words
