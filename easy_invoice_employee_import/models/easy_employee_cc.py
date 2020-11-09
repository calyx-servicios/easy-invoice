# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _

class EasyEmployeeCc(models.Model):
    _inherit = "easy.employee.cc"

### Fields
    import_line_id = fields.Many2one('easy.employee.cc.import.line', string='Imported')
### end Fields