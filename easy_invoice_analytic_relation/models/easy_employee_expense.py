# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class EasyEmployeeExpense(models.Model):
    _inherit = "easy.employee.expense"
    

### Fields
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    analytic_line_id = fields.Many2one('account.analytic.line', 'Analytic Line Move')
    product_id = fields.Many2one('product.product', 'Analytic Product')
### end Fields


    @api.multi
    def rendig(self):
        easy_employee_expense_obj = super(EasyEmployeeExpense, self).rendig()
        if easy_employee_expense_obj.analytic_account_id and easy_employee_expense_obj.amount_expense != 0.0:
            self.create_line_analytic_account_line()
        return easy_employee_expense_obj

    @api.multi
    def create_line_analytic_account_line(self,analytic=None): 
        for easy_employee_expense_obj in self:
            analytic_account_obj = easy_employee_expense_obj.analytic_account_id
            if analytic:
                analytic_account_obj = analytic
                easy_employee_expense_obj.analytic_account_id = analytic_account_obj.id

            vals = {
                    'name': easy_employee_expense_obj.description,
                    #'project_id': holiday_project.id,
                    #'task_id': holiday_task.id,
                    'account_id': analytic_account_obj.id,
                    'unit_amount': 1,
                    'product_id': easy_employee_expense_obj.product_id.id,
                    #'user_id': holiday.employee_id.user_id.id,
                    #'company_id': holiday.employee_id.user_id.id,
                    'date': easy_employee_expense_obj.date,
                    'employee_expense_id': easy_employee_expense_obj.id,
                    'amount': easy_employee_expense_obj.amount_expense  * (-1.0) ,
                    }
            line_created = self.env['account.analytic.line'].create(vals) 
            easy_employee_expense_obj.analytic_line_id = line_created.id
            self.create_message(analytic_account_obj)


        #return var_return

    @api.multi
    def create_message(self,old): # este no esta andando
        #_logger.debug('======>alert_apocryphal<======')
        self.ensure_one()
        subject = _('Se crea Movimiento Analítico')
        message = _('Crea con la cuenta Cuenta Analítica ')+_(old.name) 
        message += _(' en la linea ')+_(self.description)
        user_ids = self.env['res.users'].search([('active','=',True)])
        self.env['mail.message'].create({'message_type':'notification',
                                         'body': message,
                                         'subject': subject,
                                         'needaction_partner_ids': [(4, user.partner_id.id, None) for user in user_ids],   
                                         'model': 'easy.employee.expense',
                                         'res_id': self.id,})