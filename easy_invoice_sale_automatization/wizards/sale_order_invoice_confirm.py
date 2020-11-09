##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import re

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero

from odoo.addons import decimal_precision as dp

from werkzeug import url_encode

class SaleOrderInvoiceConfirm(models.TransientModel):
    
    _name = 'sale.order.invoice.confirm'
    _description = "Sale Order Invoice Confirm"

    @api.multi
    def action_confirm(self):  
        invoice_list = {} 
        for sale_obj in self.env['sale.order'].browse(self._context['active_ids']):  
            #recorro las ordenes
            if sale_obj.state == 'draft':
                sale_obj.action_confirm()

            if sale_obj.invoice_status == 'invoiced':
                raise ValidationError(_('You can not make a Easy Invoice from a Order Sale Invoiced'))

            # confirmo ordenes
            if not str(sale_obj.partner_id.id) in invoice_list:
                invoice_list[str(sale_obj.partner_id.id)] = self._create_partner_invoice(sale_obj)
            invoice_obj = invoice_list[str(sale_obj.partner_id.id)]
            # en invoice_obj tengo la factura la cual va a agrupar el pedido
            for line_obj in sale_obj.order_line:
                # agrego las lineas
                vals = {
                    'invoice_id': invoice_obj.id,
                    'name': line_obj.name ,
                    'price_unit': line_obj.price_unit ,
                    'uom_id':    line_obj.product_uom.id,
                    'product_id': line_obj.product_id.id,
                    'quantity': line_obj.product_uom_qty,
                    'currency_id': line_obj.currency_id.id,
                    'company_id': line_obj.company_id.id,
                }
                invoice_line_created = self.env['easy.invoice.line'].create(vals) 
            sale_obj.sale_order_invoice_ids = [(4, invoice_obj.id)]
            sale_obj.invoice_status = 'invoiced'


        for line in invoice_list:
            invoice_list[line].confirm()


    def _create_partner_invoice(self,sale_obj):
        vals = sale_obj._search_data_easy_invoice('out_invoice','draft',sale_obj.confirmation_date)
        return self.env['easy.invoice'].create(vals) 