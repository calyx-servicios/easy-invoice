# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _

class EasyPartnerCC(models.Model):
    _name = "easy.partner.cc"


    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id

## Fields
#     no se restan Anticipe/Advancement
# ANTICIPO  de clientes   + haber   anticipe
# ADELANTO a proveedores  + debe    advancement

    description = fields.Char(string='Reference/Description',)
    date = fields.Date(string='Date',)
    currency_id = fields.Many2one('res.currency', string='Currency',required=True, readonly=True, default=_default_currency,)
    partner_id = fields.Many2one('res.partner', string='Partner')
    payment_id = fields.Many2one('easy.payment', string='Payment')

    amount_anticipe = fields.Monetary(string='Anticipe',)
    amount_advancement = fields.Monetary(string='Advancement',)
    user_id = fields.Many2one('res.users', string='Salesperson',readonly=True, default=lambda self: self.env.user, copy=False)

    state = fields.Selection([('open','Open'),              
                              ('cancel','Cancel'),     
                              ], string="State",default='open')
## end Fields 


    @api.multi
    def cancel_anticipe_advancement(self):
        for rec in self:
            if rec.payment_id:
                if not rec.payment_id.recaudation_id:
                    raise ValidationError(_('No Puede cancelar Anticipos/Adelantos que no esten en una Caja(chequee que no esten arqueados).'))
                if rec.amount_anticipe > 0.0:
                    if not rec.payment_id.recaudation_id.boolean_permit_amount_negative and rec.payment_id.recaudation_id.amount_box < rec.amount_anticipe:
                        raise ValidationError(_('No puede retirar el Anticipo sin Fondos en la Caja.'))
                rec.payment_id.cancel_payment()      
            rec.state = 'cancel'
        return rec


    @api.model
    def create_recaudation_move(self,recaudation_obj,state):
        for rec in self:
            amount_total =  rec.amount_anticipe - rec.amount_advancement
            sequence_number = ''
            if state == 'deposit':
                #if not recaudation_obj.boolean_permit_amount_negative and recaudation_obj.amount_box - amount_total < 0.0:
                    #raise ValidationError(_('You cant not Retire without Funds')) 
                sequence_number = recaudation_obj.configuration_sequence_id.recaudation_deposit_sequence_id.next_by_id()
            else:
                sequence_number = recaudation_obj.configuration_sequence_id.recaudation_retire_sequence_id.next_by_id()
            
            vals = {
                'name': rec.description,
                'type': state,
                #'invoice_id': self_obj.id ,
                'amount_total':  float(rec.amount_advancement+rec.amount_anticipe),

                'amount_in': rec.amount_advancement, 
                'amount_out': rec.amount_anticipe,

                #'amount_residual': self_obj.amount_total,
                'recaudation_id':   recaudation_obj.id ,
                #'payed_id': self_obj.recaudation_id   ,
                'date_pay': rec.date   ,  
                'sequence_number': sequence_number,  

            }
            line_created = self.env['easy.payment'].create(vals) 
            rec.payment_id = line_created.id
            recaudation_obj.amount_box = recaudation_obj.amount_box + amount_total
        return line_created