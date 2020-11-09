from odoo import models, api, fields, _
from ast import literal_eval
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class EasyRecaudationRetireDeposit(models.TransientModel):

    _name = 'easy.recaudation.retire.deposit'
    _description = 'Retire/Deposit/Transfer'

### Fields
    name = fields.Text(string='Description')
    amount = fields.Float(string='Amount', )
    date = fields.Date(string='Date', )
    recaudation_id = fields.Many2one('easy.recaudation', string='Transfer to')
    type = fields.Selection([('deposit', 'Deposit'),('retire', 'Retire'),('transfer', 'Transfer')], string='Type',default='deposit')
### ends Field 

    @api.multi
    def create_move(self):
        for self_obj in self: 
            recaudation_obj = self.env['easy.recaudation'].browse(self._context.get('active_id'))
          
            if self_obj.amount <=  0.0:
                raise ValidationError(_('No se pueden realizar Movimientos en cero o Negativos.'))

            if self_obj.type == 'transfer':
                # retiro
                name_transference = recaudation_obj.configuration_sequence_id.recaudation_transfer_sequence_id.next_by_id()
                vals = {
                    'name': self_obj.name,
                    'type': 'transfer',
                    #'state': 'pending', aca la plata ya sale asique no queda en pendiente
                    'amount_in': self_obj.amount,
                    'amount_out': 0.0,
                    'amount_total': self_obj.amount*(-1),
                    'recaudation_id': recaudation_obj.id, # si tiene que mostrar en el otro lado tmb
                    'recaudation_transfer_id': recaudation_obj.id,
                    'date_pay': self_obj.date   ,  
                    'sequence_number' : name_transference,
                    #'payment_transfer_id':  aca va la relacion a la otra linea que se crea posteriormente, 
                   
                }
                line_origin = self.env['easy.payment'].create(vals) 
                recaudation_obj.subtract(self_obj.amount)
               
                vals = {
                    'name': self_obj.name,
                    'type': 'transfer',
                    'state': 'pending',
                    'amount_in':  0.0,
                    'amount_out': self_obj.amount,
                    'amount_total': self_obj.amount,
                    'sequence_number' : name_transference,
                    'payment_transfer_id': line_origin.id , 
                    'recaudation_id': self_obj.recaudation_id.id, # si tiene que mostrar en el otro lado tmb
                    'recaudation_transfer_id':self_obj.recaudation_id.id,
                    'date_pay': self_obj.date   ,    
                }
                line_detinity = self.env['easy.payment'].create(vals) 
                
                line_origin.payment_transfer_id = line_detinity.id


            if self_obj.type == 'deposit':

                vals = {
                    'name': self_obj.name,
                    'type': 'deposit',
                    'amount_in':  0.0,
                    'amount_out': self_obj.amount,
                    'sequence_number':  recaudation_obj.configuration_sequence_id.recaudation_deposit_sequence_id.next_by_id(),
                    'amount_total': self_obj.amount,
                    'recaudation_id': self._context.get('active_id'), 
                    'date_pay': self_obj.date   ,      
                }
                line_created = self.env['easy.payment'].create(vals) 
                recaudation_obj.subtract(self_obj.amount)

            if self_obj.type == 'retire':
                vals = {
                    'name': self_obj.name,
                    'type': 'retire',
                    'amount_in': self_obj.amount,
                    'amount_out': 0.0,
                    'sequence_number':  recaudation_obj.configuration_sequence_id.recaudation_retire_sequence_id.next_by_id(),
                    'amount_total': self_obj.amount *(-1),
                    'recaudation_id': self._context.get('active_id'), 
                    'date_pay': self_obj.date   ,      
                }
                line_created = self.env['easy.payment'].create(vals) 
                recaudation_obj.subtract(self_obj.amount)

        return True
