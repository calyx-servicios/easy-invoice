from odoo import models, api, fields, _
from ast import literal_eval
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class EasyInvoicePayment(models.TransientModel):

    _name = 'easy.invoice.payment'
    _description = 'Easy Invoice Payment'

    @api.model
    def default_get(self, fieldss):
        res = super(EasyInvoicePayment, self).default_get(fieldss)
        aux_amount_total = 0.0
        type_invoice = ''
        for ids in self._context['active_ids']:   
            invoice_obj = self.env['easy.invoice'].browse(ids)
            type_invoice = invoice_obj.type
            aux_amount_total += invoice_obj.residual_amount
            partner_id = invoice_obj.partner_id.id

        # if type_invoice == 'in_invoice':
        #     type_invoice = 'in_refund'
        # if type_invoice == 'out_invoice':
        #     type_invoice = 'out_refund'
 
        res.update({'total_amount': aux_amount_total})
        res.update({'amount': aux_amount_total})
        res.update({'partner_id': partner_id})
        res.update({'type_invoice': type_invoice})
        res.update({'date': fields.Date.today()})
        return res


### Fields
    recaudation_id = fields.Many2one('easy.recaudation', string='Recaudation',)
    amount = fields.Float(string='Amount', )
    date = fields.Date(string='Date', )
    total_amount = fields.Float(string='Total Amount', )
    total_amount_refunded = fields.Float(string='Total Amount Refunded', )
    type_invoice = fields.Char( string='Type Invoice', )
    partner_id = fields.Many2one('res.partner', string='Partner',)
    #refund_invoice_id = fields.Many2one('easy.invoice', string='Rectificative Invoice')
### ends Field  < >


    @api.multi
    def prepare_debt(self):
        for self_obj in self: 
            amount = self_obj.amount
            group_type = 'in_group'
            name_form = 'easy_invoice.easy_payment_in_group_form' 
            if self_obj.type_invoice in ('out_invoice','out_refund'):
                group_type = 'out_group'
                name_form = 'easy_invoice.easy_payment_out_group_form' 

            vals = {
                'state' : 'draft',
                'partner_id' : self_obj.partner_id.id,
                #'currency_id' : fields.Many2one('res.currency', string:'Currency')
                'date' : self_obj.date,
                'recaudation_id': self_obj.recaudation_id.id ,   
                'group_type':group_type, 
            }
            group_create_obj = self.env['easy.payment.group'].create(vals)     

            #for ids in self._context['active_ids']:   
            for invoice_obj in self.env['easy.invoice'].browse(self._context['active_ids']).filtered(lambda obj: obj.type in ('in_refund','out_refund')):

                if self_obj.partner_id and self_obj.partner_id.id != invoice_obj.partner_id.id:
                    raise ValidationError(_('You cant not Process invoice of different Partners of the wizard.'))

## cuando son factoras de TIPO in_invoice y sus rectificativas
                if invoice_obj.type == 'in_refund':
                    aux_amount2pay = invoice_obj.residual_amount
                    amount += aux_amount2pay
                    vals = {
                        'invoice_id' : invoice_obj.id,
                        'partner_id' : self_obj.partner_id.id,
                        #'currency_id' : fields.Many2one('res.currency', string:'Currency')
                        'amount2pay' : aux_amount2pay,
                        'in_rectificative_group_id': group_create_obj.id   ,    
                    }
                    group_line_create_obj = self.env['easy.payment.group.line'].create(vals) 

## cuando son factoras de TIPO out_invoice y sus rectificativas
                if invoice_obj.type == 'out_refund':
                    aux_amount2pay = invoice_obj.residual_amount
                    amount += aux_amount2pay
                    vals = {
                        'invoice_id' : invoice_obj.id,
                        'partner_id' : self_obj.partner_id.id,
                        #'currency_id' : fields.Many2one('res.currency', string:'Currency')
                        'amount2pay' : aux_amount2pay,
                        'out_rectificative_group_id': group_create_obj.id   ,    
                    }
                    group_line_create_obj = self.env['easy.payment.group.line'].create(vals) 

            for invoice_obj in self.env['easy.invoice'].browse(self._context['active_ids']).filtered(lambda obj: obj.type in ('in_invoice','out_invoice')):

                if amount > 0.0:
                    #invoice_obj = self.env['easy.invoice'].browse(ids)
                    if self_obj.partner_id and self_obj.partner_id.id != invoice_obj.partner_id.id:
                        raise ValidationError(_('You cant not Process invoice of different Partners of the wizard.'))

## cuando son factoras de TIPO in_invoice y sus rectificativas
                    if invoice_obj.type == 'in_invoice':
                        aux_amount2pay = invoice_obj.residual_amount
                        if invoice_obj.residual_amount > amount:
                            aux_amount2pay = amount
                            amount = 0.0
                        else:
                            amount -= aux_amount2pay
                        vals = {
                            'invoice_id' : invoice_obj.id,
                            'partner_id' : self_obj.partner_id.id,
                            #'currency_id' : fields.Many2one('res.currency', string:'Currency')
                            'amount2pay' : aux_amount2pay,
                            'in_invoice_group_id': group_create_obj.id   ,    
                        }
                        group_line_create_obj = self.env['easy.payment.group.line'].create(vals) 
            
## cuando son factoras de TIPO out_invoice y sus rectificativas
                    if invoice_obj.type == 'out_invoice':
                        aux_amount2pay = invoice_obj.residual_amount
                        if invoice_obj.residual_amount > amount:
                            aux_amount2pay = amount
                            amount = 0.0
                        else:
                            amount -= aux_amount2pay
                        vals = {
                            'invoice_id' : invoice_obj.id,
                            'partner_id' : self_obj.partner_id.id,
                            #'currency_id' : fields.Many2one('res.currency', string:'Currency')
                            'amount2pay' : aux_amount2pay,
                            'out_invoice_group_id': group_create_obj.id   ,    
                        }
                        group_line_create_obj = self.env['easy.payment.group.line'].create(vals) 
                      
            group_create_obj.control_amount()

            return {
                    'name': _('Payment Group'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'easy.payment.group',
                    'view_id': self.env.ref(name_form).id,
                    'type': 'ir.actions.act_window',
                    #'domain': [('payment_id', 'in', self.ids)],
                    'res_id': group_create_obj.id,
                    'context': {},
                }

         