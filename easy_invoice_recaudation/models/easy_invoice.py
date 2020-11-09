from odoo import api, exceptions, fields, models, _
from odoo.tools import float_is_zero, float_compare, pycompat
from odoo.tools.misc import formatLang

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from odoo.addons import decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)

class EasyInvoice(models.Model):
    _name = "easy.invoice"
    _inherit = "easy.invoice"
    

### Fields
   
    recaudation_id = fields.Many2one('easy.recaudation', string='Recaudation', ondelete='restrict')
    
### ends Field



    @api.multi
    def pay_out(self,context=None,amount2pay=None,recaudation_obj=None,date=None,payment_group_id=None):
        for self_obj in self: 
            line_created = None
            self_obj.boolean_permit_cancel = False
            if date == None:
                date = fields.Date.today()

            if recaudation_obj == None:
                raise ValidationError(_('You cant not Pay a Invoice without Recaudation. Pick one in Wizard or Invoice to continue'))
            
            if not recaudation_obj.configuration_sequence_id.invoice_out_pay_sequence_id:
                raise ValidationError(_('You cant not Pay a Invoice without Sequence'))

            if amount2pay == None:
                amount2pay = self_obj.residual_amount

            if amount2pay > self_obj.residual_amount:
                amount2pay = self_obj.residual_amount
                self_obj.write({'residual_amount':0.0,'state':'paid'})

            if amount2pay != 0.0:
                vals = {
                    'name': 'Venta',
                    'type': 'pay_out',
                    'state': 'open',
                    'invoice_id': self_obj.id ,
                    'amount_total':  float(amount2pay),
                    'amount_out': amount2pay,
                    #'amount_residual': self_obj.amount_total,
                    'recaudation_id':   recaudation_obj.id ,
                    #'payed_id': self_obj.recaudation_id   ,
                    'date_pay': date   ,  
                    'sequence_number': recaudation_obj.configuration_sequence_id.invoice_out_pay_sequence_id.next_by_id()  ,    
                    'payment_group_id': payment_group_id   ,   
                }
                line_created = self.env['easy.payment'].create(vals) 
                #vals = {'amount_box': recaudation_obj.amount_box + amount2pay,}
                recaudation_obj.amount_box = recaudation_obj.amount_box + amount2pay

            return line_created

    @api.multi
    def pay_in(self,context=None,amount2pay=None,recaudation_obj=None,date=None,payment_group_id=None):
        for self_obj in self: 
            line_created = None
            self_obj.boolean_permit_cancel = False
            if date == None:
                date = fields.Date.today()
            if recaudation_obj == None:
                raise ValidationError(_('You cant not Pay a Invoice without Recaudation. Pick one in Invoice to continue. Ref:(%s)')%self_obj.name)
    
            if not recaudation_obj.configuration_sequence_id.invoice_in_pay_sequence_id:
                raise ValidationError(_('You cant not Pay a Invoice without Sequence'))

            if amount2pay == None:
                amount2pay = self_obj.residual_amount

            if amount2pay > self_obj.residual_amount:
                amount2pay = self_obj.residual_amount
                self_obj.write({'residual_amount':0.0,'state':'paid'})
                
            if amount2pay != 0.0:
                if not recaudation_obj.boolean_permit_amount_negative and recaudation_obj.amount_box - amount2pay < 0.0:
                    raise ValidationError(_('You cant not Pay a Invoice without Funds'))

                vals = {
                    'name': 'Compra',
                    'type': 'pay_in',
                    'state': 'open',
                    'sequence_number': recaudation_obj.configuration_sequence_id.invoice_in_pay_sequence_id.next_by_id(),
                    'invoice_id': self_obj.id,
                    'amount_total': float(amount2pay) * (-1.0),
                    'amount_in': amount2pay,
                    'recaudation_id': recaudation_obj.id,
                    'date_pay': date,
                    'payment_group_id': payment_group_id,
                }
                
                line_created = self.env['easy.payment'].create(vals)
                
                #vals = {'amount_box': recaudation_obj.amount_box - amount2pay,}
                recaudation_obj.amount_box = recaudation_obj.amount_box - amount2pay
            return line_created



    @api.multi
    def boton_print_easy_invoice_payment(self):        
        return {    
            'name': _("Pago Total o Parcial de Facturas"),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'easy.invoice.payment',
            'target': 'new',
            
        }

