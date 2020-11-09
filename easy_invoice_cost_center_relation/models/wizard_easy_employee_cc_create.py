from odoo import models, api, fields, _
from ast import literal_eval
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class WizardEasyEmployeeCcCreate(models.TransientModel):

    _inherit = 'wizard.easy.employee.cc.create'
    #_description = 'Wizard Easy Employee C.C. Create'

    @api.multi
    def create_move(self):
        easy_employee_cc_obj = super(WizardEasyEmployeeCcCreate, self).create_move()
        for self_obj in self: 
            #if self_obj.type == 'advancement':
               # employee_obj = self.env['hr.employee'].browse(self._context['active_id'])
            if easy_employee_cc_obj and easy_employee_cc_obj.employee_id.employee_cc_cost_center_ids :
                vals = {
                    'name': easy_employee_cc_obj.employee_id.name,
                    'state': 'open',
                    'payment_id': easy_employee_cc_obj.payment_id.id,
                    #'state': 'open',

                    #'invoice_id': rec.invoice_residual_amount_id.invoice_id.id ,
                    'employee_cc_id': easy_employee_cc_obj.id ,
                    'date': self_obj.date,

                    'amount': self_obj.amount  *(-1.0) ,    
                    #'cost_center_ids': easy_employee_cc_obj.employee_id.employee_cc_cost_center_ids   , 
                    'partner_id': easy_employee_cc_obj.employee_id.address_home_id.id   , 

                }
                line_created = self.env['cost.center.move'].create(vals) 
                line_created.cost_center_ids = easy_employee_cc_obj.employee_id.employee_cc_cost_center_ids
                easy_employee_cc_obj.cost_center_move_id = line_created.id
        return easy_employee_cc_obj
