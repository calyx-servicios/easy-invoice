# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _

class EasyInvoice(models.Model):
    _inherit = "easy.invoice"


### Fields
    #cost_center_id = fields.Many2one('cost.center', 'Cost Center')
    #cost_center_move_id = fields.Many2one('cost.center.move', 'Cost Center Move')
### end Fields

    @api.multi
    def create_line_residual(self): 
        var_return = super(EasyInvoice, self).create_line_residual()
        for rec in self:
            for line_obj in rec.invoice_line_ids:
                line_obj.create_line_cost_center()
        return var_return

#### en teoria si borra la linea de pago se va a borrar aca pro por las dudas se tendria que extender este metodo
    @api.multi
    def cancel_invoice(self):
        var_return =  super(EasyInvoice, self).cancel_invoice()
        for self_obj in self:
            for line_obj in self_obj.invoice_line_ids:
                if line_obj.cost_center_move_id:
                    line_obj.cost_center_move_id.unlink()
        return var_return