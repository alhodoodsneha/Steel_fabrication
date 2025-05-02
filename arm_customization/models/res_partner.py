from odoo import api, models, fields, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sequence_code = fields.Char(string="Sequence")
    is_customer = fields.Boolean(string="Customer", default=False)
    is_vendor = fields.Boolean(string="vendor", default=False)
    trade_license = fields.Char(string="Trade License Number")
    expiry_date = fields.Date(string="Expiry Date")

    @api.model
    def create(self, vals):
        if not self.env.user.has_group('arm_customization.group_customer_manager'):
            raise UserError(_('You don not have the rights to create contact !!'))
        else:
            res = super(ResPartner, self).create(vals)
        return res

    def unlink(self):
        if not self.env.user.has_group('arm_customization.group_delete_user'):
            raise UserError(_("You do not have the access to delete records !!"))
        else:
            return super(ResPartner, self).unlink()
