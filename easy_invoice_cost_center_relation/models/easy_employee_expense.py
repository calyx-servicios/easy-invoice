# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class EasyEmployeeExpense(models.Model):
    _inherit = "easy.employee.expense"
    

### Fields
    #payment_cost_center_id = fields.Many2one('cost.center', 'Cost Center')
    employee_expense_cost_center_ids = fields.Many2many('cost.center', 'cost_center_employee_expense_rel', 
                                                'cost_center_id','employee_expense_id', string='Cost Center',)

    cost_center_move_id = fields.Many2one('cost.center.move', 'Cost Center Move')
### end Fields


    @api.multi
    def rendig(self):
        easy_employee_expense_obj = super(EasyEmployeeExpense, self).rendig()
       

        if easy_employee_expense_obj.employee_expense_cost_center_ids and easy_employee_expense_obj.amount_expense != 0.0:
            vals = {
                'name': easy_employee_expense_obj.employee_id.name,
                'state': 'open',
                'payment_id': easy_employee_expense_obj.payment_amount_id.id,
                #'state': 'open',

                #'invoice_id': rec.invoice_residual_amount_id.invoice_id.id ,
                'employee_expense_id': easy_employee_expense_obj.id ,
                'date': easy_employee_expense_obj.payment_amount_id.date_pay,

                'amount': easy_employee_expense_obj.amount  *(-1.0) ,    
                #'cost_center_ids': easy_employee_expense_obj.employee_expense_cost_center_ids   , 
                'partner_id': easy_employee_expense_obj.employee_id.address_home_id.id   , 

            }
            line_created = self.env['cost.center.move'].create(vals) 
            line_created.cost_center_ids = easy_employee_expense_obj.employee_expense_cost_center_ids
            easy_employee_expense_obj.cost_center_move_id = line_created.id
        return easy_employee_expense_obj