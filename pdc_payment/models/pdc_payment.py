from odoo import models, fields, api
from datetime import date, timedelta


class PdcPaymentSubmit(models.Model):
    _name = 'pdc.payment.submit'
    _description = 'PDC Submitted'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'cheque_no'

    cheque_no = fields.Char(string='Cheques Number', tracking=True)
    supplier_id = fields.Many2one('res.partner', string="Supplier", tracking=True)
    cheque_date = fields.Date(string="Cheque Date", tracking=True)
    amount = fields.Float(string="Amount", tracking=True)
    bank = fields.Char(string="Bank Name", tracking=True)
    status = fields.Selection(
        [('received', 'Received'), ('matured', 'Matured'), ('rejected', 'Bounced'), ('hold', 'Hold'),
         ('returned', 'Returned')], tracking=True, default='received',copy=False)
    reject_reason = fields.Text(string='Reject Reason', tracking=True)
    hold_reason = fields.Text(string='Hold Reason', tracking=True)
    return_reason = fields.Text(string='Return Reason', tracking=True)
    is_delayed = fields.Boolean(string='Is Delayed', compute='_compute_is_delayed')

    @api.depends('cheque_date', 'status')
    def _compute_is_delayed(self):
        for record in self:
            if record and record.cheque_date:
                if record.status == 'received' and record.cheque_date < fields.Date.today():
                    record.is_delayed = True
                else:
                    record.is_delayed = False
            else:
                record.is_delayed = False

    def action_deposit(self):
        self.status = 'matured'
        if self.status == ' matured':
            self.env['account.payment'].create({
                'payment_type': 'inbound',
                'partner_type': 'supplier',
                'partner_id': self.supplier_id.id,
                'amount': self.amount,
                'cheque_reference': self.cheque_no
            })

    def action_reject(self):
        self.status = 'rejected'
        return {
            'name': 'Reason',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'pdc.reason.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        'state': 'rejected'
                        }
        }

    def action_hold(self):
        self.status = 'hold'
        return {
            'name': 'Reason',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'pdc.reason.receive.hold.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        'type': 'submit'
                        }
        }

    def action_returned(self):
        self.status = 'returned'
        return {
            'name': 'Reason',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'pdc.reason.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        'state': 'returned'
                        }
        }

    def send_reminder_pdc_submitted(self):
        today = fields.Date.today()
        two_days_ahead = today + timedelta(days=2)
        one_day_ahead = today + timedelta(days=1)
        records = self.search([
            ('cheque_date', 'in', [two_days_ahead, one_day_ahead, today]),
            ('status', '=', 'received')
        ])
        for record in records:
            account_manager_group = self.env.ref('base_accounting_kit.group_account_manager')
            account_user_group = self.env.ref('base_accounting_kit.group_account_user')
            users_to_notify = account_manager_group.users | account_user_group.users
            for user in users_to_notify:
                if user.email and self.env.user.email:
                    subject = f"Reminder: Cheque {record.cheque_no} Due Soon"
                    body = f"""
                                   <p>Hello {record.customer_id.name},</p>
                                   <p>This is a reminder that your cheque <strong>{record.cheque_no}</strong> is due on <strong>{record.cheque_date}</strong>.</p>
                                   <p>Please ensure timely action.</p>
                                   <p>Thank you!</p>
                                   """
                    # Send the email
                    mail_values = {
                        'subject': subject,
                        'body_html': body,
                        'email_from': self.env.user.email,
                        'email_to': user.email,  # Send to customer email
                    }
                    self.env['mail.mail'].create(mail_values).send()


class PdcPaymentReceived(models.Model):
    _name = 'pdc.payment.received'
    _description = 'PDC Received'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'cheque_no'

    cheque_no = fields.Char(string='Cheques Number', tracking=True)
    customer_id = fields.Many2one('res.partner', string="Customer", tracking=True)
    cheque_date = fields.Date(string="Cheque Date", tracking=True)
    amount = fields.Float(string="Amount", tracking=True)
    bank = fields.Char(string="Bank Name", tracking=True)
    status = fields.Selection(
        [('received', 'Received'), ('matured', 'Matured'), ('rejected', 'Bounced'), ('hold', 'Hold'),
         ('returned', 'Returned')], tracking=True, default='received',copy=False)
    reject_reason = fields.Text(string='Reject Reason', tracking=True)
    hold_reason = fields.Text(string='Hold Reason', tracking=True)
    return_reason = fields.Text(string='Return Reason', tracking=True)
    is_delayed = fields.Boolean(string='Is Delayed', compute='_compute_is_delayed')

    @api.depends('cheque_date', 'status')
    def _compute_is_delayed(self):
        for record in self:
            if record and record.cheque_date:
                if record.status == 'received' and record.cheque_date < fields.Date.today():
                    record.is_delayed = True
                else:
                    record.is_delayed = False
            else:
                record.is_delayed = False

    def action_deposit(self):
        self.status = 'matured'
        self.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.customer_id.id,
            'amount': self.amount,
            'cheque_reference': self.cheque_no
        })

    def action_reject(self):
        self.status = 'rejected'
        return {
            'name': 'Reason',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'pdc.reason.receive.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        'state': 'rejected'
                        }
        }

    def action_hold(self):
        self.status = 'hold'
        return {
            'name': 'Reason',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'pdc.reason.receive.hold.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        'type': 'receive'
                        }
        }

    def action_returned(self):
        self.status = 'returned'
        return {
            'name': 'Reason',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'pdc.reason.receive.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        'state': 'returned'
                        }
        }

    def send_reminder_pdc_received(self):
        today = fields.Date.today()
        upcoming_dates = [today + timedelta(days=i) for i in range(6)]  # 0 to 5 days from today
        records = self.search([
            ('cheque_date', 'in', upcoming_dates),
            ('status', '=', 'received')
        ])
        for record in records:
            if record.customer_id.email:
                subject = f"Reminder: Cheque {record.cheque_no} Due in soon"
                body = f"""
                                <p>Hello {record.customer_id.name},</p>
                                <p>This is a reminder that cheque <strong>{record.cheque_no}</strong> is due on <strong>{record.cheque_date}</strong>.</p>
                                <p>Please ensure timely action.</p>
                                <p>Thank you!</p>
                                """
                mail_values = {
                    'subject': subject,
                    'body_html': body,
                    'email_from': self.env.user.email,
                    'email_to': record.customer_id.email,
                }
                self.env['mail.mail'].create(mail_values).send()
