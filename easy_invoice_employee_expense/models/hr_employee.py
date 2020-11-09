# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _

class HrEmployee(models.Model):
    _inherit = "hr.employee"

### Fields
    expense_line_ids = fields.One2many('easy.employee.expense', 'employee_id', string='Expense')
### end Fields
