from odoo import api, models, fields


class PdcReasonReceiveWizard(models.TransientModel):
    _name = 'pdc.reason.receive.wizard'
    _description = "Reason"

    feedback = fields.Text('Feedback')

    def action_add_feedback(self):
        payment_receive = self.env['pdc.payment.received'].browse(self.env.context['active_id'])
        if self.env.context.get('state') == 'returned':
            payment_receive.return_reason = self.feedback
        elif self.env.context.get('state') == 'hold':
            payment_receive.hold_reason = self.feedback
        else:
            payment_receive.reject_reason = self.feedback


