# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, exceptions, fields, models, _
from odoo.tools import float_is_zero, float_compare, pycompat
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class EasyPaymentGroup(models.Model):
    
    _inherit = "easy.payment.group"

### Fields
    partner_amount_advancement = fields.Monetary(string='Partner Advancement',related='partner_id.amount_advancement', readonly=True,)
    partner_amount_anticipe = fields.Monetary(string='Partner Anticipe',related='partner_id.amount_anticipe',)

    partner_amount = fields.Monetary(string='Partner Amount', )
    partner_cc_id = fields.Many2one('easy.partner.cc', string='Partner CC Line')
### end Fields


    



    @api.multi
    def processed2cancel(self):
        result_return = super(EasyPaymentGroup, self).processed2cancel()
        for rec in self:
            if rec.partner_cc_id:
                    rec.partner_cc_id.unlink()
        return result_return  
      


    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.group_type == 'in_group':
            self.partner_amount =  self.partner_amount_advancement
        if self.group_type == 'out_group':
            self.partner_amount = self.partner_amount_anticipe
        return super(EasyPaymentGroup, self).onchange_partner_id()
    
    @api.multi
    def _control_invoice_amount(self,invoice_ids):
        result_return = super(EasyPaymentGroup, self)._control_invoice_amount(invoice_ids)
        if self.partner_amount != 0.0:
            partner_amount2use = self.partner_amount
            for line_invoice_obj in invoice_ids:
                if self.group_type == 'in_group':
                    if line_invoice_obj.amount2payed > 0.0:
                        amount2pay = partner_amount2use
                        if amount2pay > line_invoice_obj.amount2payed:
                            amount2pay = line_invoice_obj.amount2payed
                        partner_amount2use -= amount2pay
                        line_invoice_obj.amount2payed -= amount2pay

                        name = self.recaudation_id.configuration_sequence_id.refund_invoice_in_pay_sequence_id.next_by_id()
                        vals = {
                            'name': name,
                            'type': 'pay_in',
                            'invoice_id': line_invoice_obj.invoice_id.id ,
                            'amount_total': float(amount2pay) * (-1.0),
                            'amount_in': amount2pay,
                            'date_pay': self.date   ,    
                            #'invoice_refund_id': rectificative_obj.invoice_id.id   , 
                            'payment_group_id': self.id   , 

                        }
                        line_created = self.env['easy.payment'].create(vals) 
            
                if self.group_type == 'out_group':
                    if line_invoice_obj.amount2payed > 0.0:
                        amount2pay = partner_amount2use
                        if amount2pay > line_invoice_obj.amount2payed:
                            amount2pay = line_invoice_obj.amount2payed
                        partner_amount2use -= amount2pay
                        line_invoice_obj.amount2payed -= amount2pay
                        
                        name = self.recaudation_id.configuration_sequence_id.refund_invoice_out_pay_sequence_id.next_by_id()
                        vals = {
                            'name': name,
                            'type': 'pay_in',
                            'invoice_id': line_invoice_obj.invoice_id.id ,
                            'amount_total': float(amount2pay),
                            'amount_out': amount2pay  ,
                            'date_pay': self.date   ,    
                            #'invoice_refund_id': rectificative_obj.invoice_id.id   ,    
                            'payment_group_id': self.id   , 
                        }
                        line_created = self.env['easy.payment'].create(vals) 
        return result_return




    @api.multi
    def prepared2draft(self):
        for rec in self:
            if rec.partner_cc_id:
                rec.partner_cc_id.unlink()
        return super(EasyPaymentGroup, self).prepared2draft()

    @api.multi
    def control_amount(self):
        var_return  = super(EasyPaymentGroup, self).control_amount()
        
        for rec in self:
            rec.amount_money -= rec.partner_amount
            if rec.amount_money < 0.0 :
                raise ValidationError(_('You cant not Prepare a Group with Amount Money in 0 or Negative.-'))
        return var_return

    @api.multi
    def sum_amount_money_defined(self,amount_total_rectificative):
        var_return  = super(EasyPaymentGroup, self).sum_amount_money_defined(amount_total_rectificative)
        # in    partner_amount_advancement
        # out   partner_amount_anticipe
        for rec in self:
            if rec.group_type and rec.group_type in ('in_group'):
                if rec.partner_amount_advancement >= rec.partner_amount:
                    vals = {
                        'description':'Compra Preparada',
                        'date': rec.date,
                        'partner_id': rec.partner_id.id ,
                        'amount_anticipe' : 0.0,
                        'amount_advancement' : rec.partner_amount * (-1),
                    }
                    rec.partner_cc_id = (self.env['easy.partner.cc'].create(vals)).id
                else:
                    raise ValidationError(_('No Puede usar un monto en Mayor al Adelanto que posee el Proveedor.-'))

            if rec.group_type and rec.group_type in ('out_group'):
                if rec.partner_amount_anticipe >= rec.partner_amount:
                    vals = {
                        'description':'Venta Preparada',
                        'date': rec.date,
                        'partner_id': rec.partner_id.id ,
                        'amount_anticipe' : rec.partner_amount * (-1),
                        'amount_advancement' : 0.0,
                    }
                    rec.partner_cc_id = (self.env['easy.partner.cc'].create(vals)).id
                else:
                    raise ValidationError(_('No Puede usar un monto en Mayor al Anticipo que posee el Cliente.-'))

        return  (var_return + rec.partner_amount)








    # @api.multi
    # def processed2cancel(self):
    #     result_return = super(EasyPaymentGroup, self).processed2cancel()
    #     for rec in self:
    #         if rec.partner_cc_id:
    #                 rec.partner_cc_id.unlink()
    #     return result_return  
      
    # @api.multi
    # @api.onchange('partner_id')
    # def onchange_partner_id(self):

    #     if self.group_type == 'in_group':
    #         self.partner_amount =  self.partner_amount_advancement
    #     if self.group_type == 'out_group':
    #         self.partner_amount = self.partner_amount_anticipe

    #     return super(EasyPaymentGroup, self).onchange_partner_id()

    
    # @api.multi
    # def _control_invoice_amount(self,invoice_ids):
    #     result_return = super(EasyPaymentGroup, self)._control_invoice_amount(invoice_ids)
    #     if self.partner_amount != 0.0:
    #         partner_amount2use = self.partner_amount
    #         for line_invoice_obj in invoice_ids:
    #             if self.group_type == 'in_group':
    #                 if line_invoice_obj.amount2payed > 0.0:
    #                     amount2pay = partner_amount2use
    #                     if amount2pay > line_invoice_obj.amount2payed:
    #                         amount2pay = line_invoice_obj.amount2payed
    #                     partner_amount2use -= amount2pay
    #                     line_invoice_obj.amount2payed -= amount2pay

    #                     name = self.recaudation_id.configuration_sequence_id.refund_invoice_in_pay_sequence_id.next_by_id()
    #                     vals = {
    #                         'name': name,
    #                         'type': 'pay_in',
    #                         'invoice_id': line_invoice_obj.invoice_id.id ,
    #                         'amount_total': float(amount2pay) * (-1.0),
    #                         'amount_in': amount2pay,
    #                         'date_pay': self.date   ,    
    #                         #'invoice_refund_id': rectificative_obj.invoice_id.id   , 
    #                         'payment_group_id': self.id   , 

    #                     }
    #                     line_created = self.env['easy.payment'].create(vals) 
            
    #             if self.group_type == 'out_group':
    #                 if line_invoice_obj.amount2payed > 0.0:
    #                     amount2pay = partner_amount2use
    #                     if amount2pay > line_invoice_obj.amount2payed:
    #                         amount2pay = line_invoice_obj.amount2payed
    #                     partner_amount2use -= amount2pay
    #                     line_invoice_obj.amount2payed -= amount2pay
                        
    #                     name = self.recaudation_id.configuration_sequence_id.refund_invoice_out_pay_sequence_id.next_by_id()
    #                     vals = {
    #                         'name': name,
    #                         'type': 'pay_in',
    #                         'invoice_id': line_invoice_obj.invoice_id.id ,
    #                         'amount_total': float(amount2pay),
    #                         'amount_out': amount2pay  ,
    #                         'date_pay': self.date   ,    
    #                         #'invoice_refund_id': rectificative_obj.invoice_id.id   ,    
    #                         'payment_group_id': self.id   , 
    #                     }
    #                     line_created = self.env['easy.payment'].create(vals) 
    #     return result_return




    # @api.multi
    # def _sum_amount_money_defined(self,amount_total_rectificative):
    #     var_return  = super(EasyPaymentGroup, self)._sum_amount_money_defined(amount_total_rectificative)
    #     # in    partner_amount_advancement
    #     # out   partner_amount_anticipe
    #     for rec in self:
    #         if rec.group_type and rec.group_type in ('in_group'):
    #             if rec.partner_amount_advancement >= rec.partner_amount:
    #                 vals = {
    #                     'description':'Compra Preparada',
    #                     'date': rec.date,
    #                     'partner_id': rec.partner_id.id ,
    #                     'amount_anticipe' : 0.0,
    #                     'amount_advancement' : rec.partner_amount * (-1),
    #                 }
    #                 rec.partner_cc_id = (self.env['easy.partner.cc'].create(vals)).id
    #             else:
    #                 raise ValidationError(_('No Puede usar un monto en Mayor al Adelanto que posee el Proveedor.-'))

    #         if rec.group_type and rec.group_type in ('out_group'):
    #             if rec.partner_amount_anticipe >= rec.partner_amount:
    #                 vals = {
    #                     'description':'Venta Preparada',
    #                     'date': rec.date,
    #                     'partner_id': rec.partner_id.id ,
    #                     'amount_anticipe' : rec.partner_amount * (-1),
    #                     'amount_advancement' : 0.0,
    #                 }
    #                 rec.partner_cc_id = (self.env['easy.partner.cc'].create(vals)).id
    #             else:
    #                 raise ValidationError(_('No Puede usar un monto en Mayor al Anticipo que posee el Cliente.-'))

    #     return  (var_return + rec.partner_amount)


           

