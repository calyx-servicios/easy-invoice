from odoo import models, api, fields, _
from ast import literal_eval
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class WizardEasyEmployeeCcConfirm(models.TransientModel):

    _name = 'wizard.easy.employee.cc.confirm'
    _description = 'Wizard Easy Employee C.C. Confirm'

### Fields
    amount = fields.Float(string='Amount', )
    amount_total = fields.Float(string='Amount Total', )
    recaudation_id = fields.Many2one('easy.recaudation', string='Recaudation')
### ends Field 



    @api.multi
    def create_move(self):
        for self_obj in self: 
            line_cc_obj = None
            if self_obj.amount <=0.0:
                raise ValidationError(_('You must put an amount greater than zero'))
            if  self_obj.amount_total  < self_obj.amount :
                raise ValidationError(_('You must put an amount equal or less of Amount Total'))

            for line_cc_obj in self.env['easy.employee.cc'].browse(self._context['active_ids']):  
                if line_cc_obj.amount_residual_payment <= self_obj.amount:
                    # pago TODO lo q tenia para pagar
                    amount2pay = line_cc_obj.amount_residual_payment
                    line_cc_obj.amount_residual_payment = 0.0
                    line_cc_obj.state = 'done'
                    line_cc_obj.recaudation_id = self_obj.recaudation_id.id
                    line_cc_obj.create_recaudation_move(amount2pay=amount2pay)
                else:
                    # pago PARTE lo q tenia para pagar
                    amount2pay = self_obj.amount
                    line_cc_obj.amount_residual_payment =  line_cc_obj.amount_residual_payment-self_obj.amount
                    #line_cc_obj.state = 'done'
                    line_cc_obj.recaudation_id = self_obj.recaudation_id.id
                    line_cc_obj.create_recaudation_move(amount2pay=amount2pay)
                    
                return line_cc_obj
