# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"
            



    @api.multi
    def _create_line_easy_invoice(self,invoice_created):
        for line_obj in self.order_line:
            vals = {
                'invoice_id': invoice_created.id,
                'name': line_obj.name ,
                'price_unit': line_obj.price_unit ,
                'uom_id':    line_obj.product_uom.id,
                'product_id': line_obj.product_id.id,
                'quantity': line_obj.product_uom_qty,
                'currency_id': line_obj.currency_id.id,
                'company_id': line_obj.company_id.id,
                #'cost_center_ids': line_obj.cost_center_ids ,
            }
            invoice_line_created = self.env['easy.invoice.line'].create(vals)
            if line_obj.order_line_cost_center_ids:
                invoice_line_created.invoice_line_cost_center_ids = line_obj.order_line_cost_center_ids
