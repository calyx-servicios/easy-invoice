# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError, AccessError, UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _prepare_line_easy_invoice(self, invoice_created):
        vals = {
            'invoice_id': invoice_created.id,
            'name': self.name,
            'price_unit': self.price_unit,
            'uom_id':    self.product_uom.id,
            'product_id': self.product_id.id,
            'quantity': self.product_uom_qty,
            'currency_id': self.currency_id.id,
            'company_id': self.company_id.id,
        }
        return vals


class SaleOrder(models.Model):
    _inherit = "sale.order"

    invoice_ids = fields.One2many(
        'easy.invoice', 'sale_order_id', string='Invoice Lines',)

    sale_order_invoice_ids = fields.Many2many('easy.invoice', 'easy_invoice_sale_order_rel', 'sale_order_id',
                                              'invoice_id', string='Invoice Lines')

    @api.multi
    def _search_data_easy_invoice(self, ttype, state, date_due):
        var_return = None
        for self_obj in self:
            var_return = {
                'type': ttype,
                'state': state,
                'partner_id':    self_obj.partner_id.id,
                'company_id': self_obj.company_id.id,
                'sale_order_id': self_obj.id,
                'pricelist_id': self_obj.pricelist_id.id,
                'note': self_obj.note,
            }
        return var_return

    @api.multi
    def _create_line_easy_invoice(self, invoice_created):
        for line_obj in self.order_line:
            vals = line_obj._prepare_line_easy_invoice(invoice_created)
            invoice_line_created = self.env['easy.invoice.line'].create(vals)

    @api.multi
    def create_easy_invoice(self):
        for self_obj in self:
            date_due = self_obj.confirmation_date
            if self.payment_term_id:
                pterm = self.payment_term_id
                pterm_list = pterm.with_context(currency_id=self.company_id.currency_id.id).compute(
                    value=1, date_ref=self_obj.confirmation_date)[0]
                date_due = max(line[0] for line in pterm_list)
            vals = self._search_data_easy_invoice(
                'out_invoice', 'draft', date_due)
            invoice_created = self.env['easy.invoice'].create(vals)

            self._create_line_easy_invoice(invoice_created)

            self_obj.sale_order_invoice_ids = [(4, invoice_created.id)]
            self_obj.invoice_status = 'invoiced'
            return {
                'name': _('Easy Invoice'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'easy.invoice',
                'view_id': self.env.ref('easy_invoice.easy_invoice_customer_form').id,
                'type': 'ir.actions.act_window',
                #'domain': [('payment_id', 'in', self.ids)],
                'res_id': invoice_created.id,
                'context': {'invoice_obj': invoice_created},
            }

    @api.multi
    def action_cancel(self):
        for easy in self:
            denied = False
            for invoice in self.sale_order_invoice_ids:
                if invoice.state not in ['draft', 'cancel']:
                    denied = True
            if denied:
                raise UserError(
                    _('You cannot cancel a Sale Order with confirmed easy invoices'))
            else:
                res = super(SaleOrder, easy).action_cancel()
                for invoice in self.sale_order_invoice_ids:
                    if invoice.state in ['draft']:
                        invoice.cancel_invoice()
                return res
