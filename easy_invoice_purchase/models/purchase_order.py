# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"


    #easy_invoice_id = fields.Many2one('easy.invoice', string='Easy Invoice',)

    easy_invoice_ids = fields.One2many('easy.invoice', 'purchase_order_id', string='Invoice Lines',)
    


    @api.multi
    def create_easy_invoice(self):
        for self_obj in self:
            self_obj.invoice_status = 'invoiced'
            vals = {
                'type': 'in_invoice',
                'state': 'draft' ,
                'partner_id':    self_obj.partner_id.id,
                'company_id': self_obj.company_id.id,
                'purchase_order_id': self_obj.id,
                'date_invoice': self_obj.date_order,
                'date_expiration': self_obj.date_order,
            }
            invoice_created = self.env['easy.invoice'].create(vals) 
            #self_obj.easy_invoice_id = invoice_created.id

            for line_obj in self_obj.order_line:
                vals = {
                    'invoice_id': invoice_created.id,
                    'name': line_obj.product_id.name ,
                    'price_unit': line_obj.price_unit ,
                    'uom_id':    line_obj.product_uom.id,
                    'product_id': line_obj.product_id.id,
                    'quantity': line_obj.product_qty,
                    'currency_id': line_obj.currency_id.id,
                    'company_id': line_obj.company_id.id,
                }
                invoice_line_created = self.env['easy.invoice.line'].create(vals) 
                 
            return {
                'name': _('Easy Invoice'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'easy.invoice',
                'view_id': self.env.ref('easy_invoice.easy_invoice_supplier_form').id, #easy_invoice_customer_form
                'type': 'ir.actions.act_window',
                #'domain': [('payment_id', 'in', self.ids)],
                'res_id': invoice_created.id,
                'context': {},
            }