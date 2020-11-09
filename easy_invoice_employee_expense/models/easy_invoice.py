# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _

class EasyInvoice(models.Model):
    _inherit = "easy.invoice"

### Fields
    expense_id = fields.Many2one('easy.employee.expense', string='Expense')
### end Fields
