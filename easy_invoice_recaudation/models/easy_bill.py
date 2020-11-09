from odoo import api, exceptions, fields, models, _
from odoo.tools import float_is_zero, float_compare, pycompat
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class EasyBill(models.Model):

    _name = "easy.bill"
    

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id

    value  = fields.Monetary(string='Bill Value')
    currency_id = fields.Many2one('res.currency', string='Currency',
        required=True, readonly=True, default=_default_currency)
    company_id = fields.Many2one('res.company', string='Company', change_default=True,
        required=True,  
        default=lambda self: self.env['res.company']._company_default_get('easy.bill'))


    _rec_name='value'
    _sql_constraints = [
        ('value_uniq', 'unique(value, company_id, currency_id)', 'Bill Value must be unique per Currency and Company!'),
    ]