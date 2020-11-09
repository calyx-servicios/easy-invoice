# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _

class EasyInvoiceLine(models.Model):
    _inherit = "easy.invoice.line"


### Fields
    #cost_center_id = fields.Many2one('cost.center', 'Cost Center')
    invoice_line_cost_center_ids = fields.Many2many('cost.center', 'cost_center_invoice_line_rel', 
                                            'cost_center_id','invoice_line_id', string='Cost Center',)

    cost_center_move_id = fields.Many2one('cost.center.move', 'Cost Center Move')
### end Fields

    @api.multi
    def create_line_cost_center(self): 
        #var_return = super(EasyInvoiceLine, self).create_line_residual()
        for rec in self:
            if rec.invoice_line_cost_center_ids:
                amount2use = rec.price_subtotal
                #if rec.invoice_id.type in ('in_invoice','out_refund'):
                    #amount2use = amount2use *(-1.0)
                vals = {
                    'name': rec.product_id.name,
                    'state_easy_invoice': 'open',
                    'payment_id': rec.invoice_id.invoice_residual_amount_id.id,
                    #'state': 'open',
                    'invoice_id': rec.invoice_id.id ,
                    #'partner_cc_id': line_invoice_obj.invoice_id.id ,
                    'date': rec.invoice_id.date_invoice,
                    'amount': amount2use   ,    
                    #'invoice_line_cost_center_ids': rec.invoice_line_cost_center_ids  , 
                    'partner_id': rec.invoice_id.partner_id.id   , 
                }
                line_created = self.env['cost.center.move'].create(vals) 
                line_created.cost_center_ids = rec.invoice_line_cost_center_ids
                rec.cost_center_move_id = line_created.id

        #return var_return
