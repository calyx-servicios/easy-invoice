# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
            
    #cost_center_ids = fields.Many2one('cost.center', 'Cost Center')
    order_line_cost_center_ids = fields.Many2many('cost.center', 'cost_center_order_line_rel', 
                                                    'cost_center_id','order_line_id', string='Cost Center',)
   