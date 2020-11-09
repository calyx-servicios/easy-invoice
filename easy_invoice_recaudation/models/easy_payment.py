from odoo import api, exceptions, fields, models, _
from odoo.tools import float_is_zero, float_compare, pycompat
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class EasyPayment(models.Model):

    _name = "easy.payment"
    _inherit = "easy.payment"
   

### Fields
    payment_transfer_id = fields.Many2one('easy.payment', string='Payment Pending')
    payment_group_id = fields.Many2one('easy.payment.group', string='Payment Group')
    
    recaudation_id = fields.Many2one('easy.recaudation', string='Recaudation Reference', ondelete='restrict')
    recaudation_transfer_id = fields.Many2one('easy.recaudation', string='Recaudation Transfer', ondelete='restrict')
    recaudation_history_id = fields.Many2one('easy.recaudation', string='Recaudation Reference History', ondelete='restrict')
    recaudation_close_id = fields.Many2one('easy.recaudation', string='Recaudation Reference Close', ondelete='restrict')

    type = fields.Selection([('transfer','Transfer'),
                             ('arch','Arch'),
                             ('pay_in', 'Pay In'),
                             ('pay_out', 'Pay Out'),
                             ('deposit', 'Deposit'),
                             ('retire', 'Retire')], string='Type')
    
    

### ends Field   

## metodos para los reportes.-
    @api.multi
    def get_amount(self):
        if self.amount_total<0.0:
            return self.amount_total*(-1.0)
        else:
            return self.amount_total

    @api.multi
    def get_caja_destino(self):
        if self.type == 'transfer':
            if self.amount_total<0.0:
                return self.payment_transfer_id.recaudation_id.name
            else:
                return self.recaudation_id.name
        if self.type == 'deposit':
            return '-'
        if self.type == 'retire':
            return '-'

    @api.multi
    def get_caja_origen(self):
        if self.type == 'transfer':
            if self.amount_total<0.0:
                return self.recaudation_id.name
            else:
                return self.payment_transfer_id.recaudation_id.name

        if self.type == 'deposit':
            if self.recaudation_id:
                return self.recaudation_id.name
            elif self.recaudation_history_id:
                return self.recaudation_history_id.name
        if self.type == 'retire':
            if self.recaudation_id:
                return self.recaudation_id.name
            elif self.recaudation_history_id:
                return self.recaudation_history_id.name
        return '-'
## metodos para los reportes.-

    @api.multi
    def accept_transfer(self):
        for self_obj in self: 
            self_obj.open()
            #self_obj.payment_transfer_id.open()
            self_obj.recaudation_transfer_id.add(self_obj.amount_total)
            #self_obj.recaudation_id = self_obj.recaudation_transfer_id.id

            

    @api.multi
    def cancel_transfer(self):
        for self_obj in self: 
            self_obj.cancel()
            self_obj.payment_transfer_id.recaudation_transfer_id.add(self_obj.amount_total)
            self_obj.payment_transfer_id.cancel()

    
    
