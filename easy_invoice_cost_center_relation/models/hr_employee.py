
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _

class HrEmployee(models.Model):
    _inherit = "hr.employee"


### Fields
    #payment_cost_center_id = fields.Many2one('cost.center', 'Cost Center')
    employee_cc_cost_center_ids = fields.Many2many('cost.center', 'cost_center_employee_cc_rel', 
                                                'cost_center_id','employee_cc_id', string='Cost Center',)

    #cost_center_move_id = fields.Many2one('cost.center.move', 'Cost Center Move')
### end Fields

   