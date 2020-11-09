from odoo import api, exceptions, fields, models, _
from odoo.tools import float_is_zero, float_compare, pycompat
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class EasySequence(models.Model):

    _name = "easy.sequence"
    _description = "Easy Sequence"
    
### Fields
    name = fields.Char(string='Name', required=True)
    
    invoice_out_confirm_sequence_id = fields.Many2one('ir.sequence',  string="Out Invoice Confirm Sequence")
    invoice_out_pay_sequence_id = fields.Many2one('ir.sequence',  string="Out Invoice Pay Sequence")
    invoice_in_confirm_sequence_id = fields.Many2one('ir.sequence',  string="In Invoice Confirm Sequence")
    invoice_in_pay_sequence_id = fields.Many2one('ir.sequence',  string="In Invoice Pay Sequence")

    debit_invoice_in_confirm_sequence_id = fields.Many2one('ir.sequence',  string="Debit In Invoice Confirm Sequence")
    debit_invoice_in_pay_sequence_id = fields.Many2one('ir.sequence',  string="Debit In Invoice Pay Sequence")
    debit_invoice_out_confirm_sequence_id = fields.Many2one('ir.sequence',  string="Debit Out Invoice Confirm Sequence")
    debit_invoice_out_pay_sequence_id = fields.Many2one('ir.sequence',  string="Debit Out Invoice Pay Sequence")


    refund_invoice_out_confirm_sequence_id = fields.Many2one('ir.sequence',  string="Refund Out Invoice Confirm Sequence")
    refund_invoice_out_pay_sequence_id = fields.Many2one('ir.sequence',  string="Refund Out Invoice Pay Sequence")
    refund_invoice_in_confirm_sequence_id = fields.Many2one('ir.sequence',  string="Refund In Invoice Confirm Sequence")
    refund_invoice_in_pay_sequence_id = fields.Many2one('ir.sequence',  string="Refund in Invoice Pay Sequence")
### ends Field   

