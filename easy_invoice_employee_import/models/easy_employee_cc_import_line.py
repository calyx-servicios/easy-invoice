# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class EasyEmployeeCcImportLine(models.Model):

    _description = "Employee Cc Import Line"
    _name = "easy.employee.cc.import.line"


    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id

## Fields 
    name = fields.Char(string='Reference/Description',)
    cc_import_id = fields.Many2one('easy.employee.cc.import', string='Import Related')
    cc_line_id = fields.Many2one('easy.employee.cc', string='C.C. Line')
    employee_id = fields.Many2one('hr.employee',  string='Employee')
    amount = fields.Monetary(string='Amount',)
    
    currency_id = fields.Many2one('res.currency', string='Currency',required=True, readonly=True, default=_default_currency,)
## end Fields 