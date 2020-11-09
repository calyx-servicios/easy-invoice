from odoo import api, exceptions, fields, models, _
from odoo.tools import float_is_zero, float_compare, pycompat
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class EasyPayment(models.Model):

    _name = "easy.payment"
    _description = "Easy Payment"
    _order = "date_pay desc,id desc"

### Fields
    name = fields.Text(string='Description')
    sequence_number = fields.Char(string='Sequence Number',)
    
    # type = fields.Integer(string='Type',default=1)
    
    invoice_id = fields.Many2one('easy.invoice', string='Invoice Reference', ondelete='cascade')
    amount_total = fields.Float(string='Amount Total',  help="Amount Total")
    amount_in = fields.Float(string='Amount In', )
    amount_out = fields.Float(string='Amount Out', )
    date_pay = fields.Date(string='Date Pay', )

    invoice_refund_id = fields.Many2one('easy.invoice', string='Invoice Refund', ondelete='cascade')



    type = fields.Selection([('pay_in', 'Pay In'),
                              ('pay_out', 'Pay Out')
                              ], string='Status')

    state = fields.Selection([('open', 'Open'),
                              ('pending', 'Pending'),
                              ('cancel', 'Cancel'),
                              ], string='State',default='open', required=True)
### ends Field   


    @api.multi
    def cancel_payment(self):
        for payment in self:
            payment.write({'state': 'cancel'})

    @api.multi
    def cancel(self):
        self.cancel_payment()

    @api.multi
    def open(self):
        for payment in self:
            payment.write({'state': 'open'})
        
        # if self.state in ('pay_in','pay_out'):
        #     #self.amount_total = 0.0
        #     self.state = 'cancel'
        # else:
        #     raise Warning(_('No puede Cancelar un Pago que no sea de tipo Pay in o Pay Out.'))
    
