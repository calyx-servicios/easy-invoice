
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _

class HrEmployee(models.Model):
    _inherit = "hr.employee"


### Fields
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account Payment CC')
    product_id = fields.Many2one('product.product', 'Analytic Product')
### end Fields

   