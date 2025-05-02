from odoo import api, models, fields


class PdcReasonReceiveHoldWizard(models.TransientModel):
    _name = 'pdc.reason.receive.hold.wizard'
    _description = "Reason"

    feedback = fields.Text('Feedback')
    next_date = fields.Date(string="Date")

    def action_add_feedback(self):
        if self.env.context.get('type') == 'receive':
            payment_receive = self.env['pdc.payment.received'].browse(self.env.context['active_id'])
            payment_receive.hold_reason = self.feedback
            payment_receive.cheque_date = self.next_date
        else:
            payment_receive = self.env['pdc.payment.submit'].browse(self.env.context['active_id'])
            payment_receive.hold_reason = self.feedback
            payment_receive.cheque_date = self.next_date
