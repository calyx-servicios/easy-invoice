from odoo import models, api, fields, _
from ast import literal_eval
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class WizardEditAnalyticAccount(models.TransientModel):

    _name = 'wizard.edit.analytic.account'
    _description = 'Wizard Edit Analytic Account'

### Fields
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    invoice_line_id = fields.Many2one('easy.invoice.line', string='Invoice Line',  )
    employee_cc_id = fields.Many2one('easy.employee.cc', string='Employee CC', )
    employee_expense_id = fields.Many2one('easy.employee.expense', string='Employee Expense', )
### ends Field 

    @api.multi
    def edit_analytic_account(self):
        for self_obj in self: 
            if self_obj.invoice_line_id:
                self_obj.invoice_line_id.edit_analytic_line(self_obj.analytic_account_id)
            if self_obj.employee_cc_id:
                self_obj.employee_cc_id.edit_analytic_line(self_obj.analytic_account_id)
            if self_obj.employee_expense_id:
                self_obj.employee_expense_id.edit_analytic_line(self_obj.analytic_account_id)
        