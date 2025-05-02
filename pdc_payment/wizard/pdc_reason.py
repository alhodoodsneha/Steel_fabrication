from odoo import api, models, fields


class PdcReasonWizard(models.TransientModel):
    _name = 'pdc.reason.wizard'
    _description = "Reason"

    feedback = fields.Text('Feedback')

    def action_add_feedback(self):
        payment_submit = self.env['pdc.payment.submit'].browse(self.env.context['active_id'])
        if self.env.context.get('state') == 'returned':
            payment_submit.return_reason = self.feedback
        elif self.env.context.get('state') == 'hold':
            payment_submit.hold_reason = self.feedback
        else:
            payment_submit.reject_reason = self.feedback

