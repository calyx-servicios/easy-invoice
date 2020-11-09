from odoo import api, exceptions, fields, models, _
from odoo.tools import float_is_zero, float_compare, pycompat
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class EasySequence(models.Model):

    _name = "easy.sequence"
    _inherit = "easy.sequence"
    
### Fields
    recaudation_transfer_sequence_id = fields.Many2one('ir.sequence',  string="Recaudation Transference Sequence")
    recaudation_deposit_sequence_id = fields.Many2one('ir.sequence',  string="Recaudation Deposit Sequence")
    recaudation_retire_sequence_id = fields.Many2one('ir.sequence',  string="Recaudation Retire Sequence")

    payment_group_sequence_in_id = fields.Many2one('ir.sequence',  string="Payment Group Sequence In")
    payment_group_sequence_out_id = fields.Many2one('ir.sequence',  string="Payment Group Sequence Out")
### ends Field   

