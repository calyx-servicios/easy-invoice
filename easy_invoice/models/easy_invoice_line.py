from odoo import api, exceptions, fields, models, _
from odoo.tools import float_is_zero, float_compare, pycompat
from odoo.tools.misc import formatLang

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from odoo.addons import decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)


class EasyInvoiceLine(models.Model):
    _name = "easy.invoice.line"
    _description = "Easy Invoice Line"
    
    @api.one
    @api.depends('price_unit', 'quantity', 'product_id', )
    def _compute_price(self):
        price = self.price_unit * (1 - (0.0) / 100.0)

        self.price_subtotal = price_subtotal_signed = round(self.quantity * price, 2)
        self.price_total = self.price_subtotal
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign

### Fields
    name = fields.Char(string='Description')
    sequence = fields.Integer(default=10,
        help="Gives the sequence of this line when displaying the invoice.")
    uom_id = fields.Many2one('product.uom', string='Unit of Measure',
        ondelete='set null', index=True, oldname='uos_id')
    product_id = fields.Many2one('product.product', string='Product',
        ondelete='restrict', index=True)
    price_unit = fields.Float(string='Unit Price', required=True, digits=dp.get_precision('Product Price'))
    price_subtotal = fields.Monetary(string='Amount',
        store=True, readonly=True, compute='_compute_price', help="Total amount without taxes")
    price_subtotal_signed = fields.Monetary(string='Amount Signed',
        store=True, readonly=True, compute='_compute_price',
        help="Total amount in the currency of the company, negative for credit note.")
    quantity = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'),
        required=True, default=1)
    company_id = fields.Many2one('res.company', string='Company',
        related='invoice_id.company_id', store=True, readonly=True, related_sudo=False)
    
    currency_id = fields.Many2one('res.currency', related='invoice_id.currency_id', store=True, related_sudo=False)


    invoice_id = fields.Many2one('easy.invoice', string='Invoice Reference',ondelete='cascade', index=True)

    
    invoice_state = fields.Selection(string='Invoice State',
        related='invoice_id.state',)

### ends Field

    def _set_currency(self):
        company = self.invoice_id.company_id
        currency = self.invoice_id.currency_id
        if company and currency:
            if company.currency_id != currency:
                self.price_unit = self.price_unit * currency.with_context(dict(self._context or {}, date=self.invoice_id.date_invoice)).rate


    @api.onchange('product_id')
    def _onchange_product_id(self):
        domain = {}
        if not self.invoice_id:
            return

        part = self.invoice_id.partner_id
        company = self.invoice_id.company_id
        currency = self.invoice_id.currency_id
        type = self.invoice_id.type

        if not part:
            warning = {
                    'title': _('Warning!'),
                    'message': _('You must first select a partner!'),
                }
            return {'warning': warning}

        if not self.product_id:
            if type not in ('in_invoice', 'in_refund'):
                self.price_unit = 0.0
            domain['uom_id'] = []
        else:
            if part.lang:
                product = self.product_id.with_context(lang=part.lang)
            else:
                product = self.product_id
            self.name = product.partner_ref
            if type in ('in_invoice', 'in_refund'):
                if product.description_purchase:
                    self.name += '\n' + product.description_purchase
            else:
                if product.description_sale:
                    self.name += '\n' + product.description_sale

            if not self.uom_id or product.uom_id.category_id.id != self.uom_id.category_id.id:
                self.uom_id = product.uom_id.id
            domain['uom_id'] = [('category_id', '=', product.uom_id.category_id.id)]

            if self.invoice_id.type in ('in_invoice', 'in_refund'):
                prec = self.env['decimal.precision'].precision_get('Product Price')
                if not self.price_unit or float_compare(self.price_unit, self.product_id.standard_price, precision_digits=prec) == 0:
                    self.price_unit = self.product_id.standard_price
                    self._set_currency()
            else:
                self.price_unit = self.product_id.lst_price
                self._set_currency()

            self.price_unit
            if company and currency:
                if self.uom_id and self.uom_id.id != product.uom_id.id:
                    self.price_unit = product.uom_id._compute_price(self.price_unit, self.uom_id)

            self.name = self.product_id.name
        return {'domain': domain}
