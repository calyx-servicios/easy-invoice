
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _

class EasyEmployeeCC(models.Model):
    _inherit = "easy.employee.cc"


### Fields
    #cost_center_id = fields.Many2one('cost.center', 'Cost Center')
    cost_center_move_id = fields.Many2one('cost.center.move', 'Cost Center Move')
### end Fields

   