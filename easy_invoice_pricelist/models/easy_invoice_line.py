# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.addons import decimal_precision as dp

class EasyInvoiceLine(models.Model):

    _inherit = "easy.invoice.line"

    price_unit_show = fields.Float(string='Unit Price Show', digits=dp.get_precision('Product Price Show'))

    @api.multi
    def _get_display_price(self, product):
        # TO DO: move me in master/saas-16 on sale.order
        if self.invoice_id.pricelist_id.discount_policy == 'with_discount':
            return product.with_context(pricelist=self.invoice_id.pricelist_id.id).price
        product_context = dict(self.env.context, partner_id=self.invoice_id.partner_id.id,
                               date=self.invoice_id.date_invoice, uom=self.uom_id.id)
        final_price, rule_id = self.invoice_id.pricelist_id.with_context(product_context).get_product_price_rule(
            self.product_id, self.quantity or 1.0, self.invoice_id.partner_id)
        base_price, currency_id = self.with_context(product_context)._get_real_price_currency(
            product, rule_id, self.quantity, self.uom_id, self.invoice_id.pricelist_id.id)
        if currency_id != self.invoice_id.pricelist_id.currency_id.id:
            base_price = self.env['res.currency'].browse(currency_id).with_context(
                product_context).compute(base_price, self.invoice_id.pricelist_id.currency_id)
        # negative discounts (= surcharge) are included in the display price
        return max(base_price, final_price)

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'uom_id': []}}

        vals = {}
        domain = {'uom_id': [
            ('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.uom_id or (self.product_id.uom_id.id != self.uom_id.id):
            vals['uom_id'] = self.product_id.uom_id
            vals['quantity'] = 1.0

        product = self.product_id.with_context(
            lang=self.invoice_id.partner_id.lang,
            partner=self.invoice_id.partner_id.id,
            quantity=vals.get('quantity') or self.quantity,
            date=self.invoice_id.date_invoice,
            pricelist=self.invoice_id.pricelist_id.id,
            uom=self.uom_id.id
        )

        result = {'domain': domain}

        title = False
        message = False
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False
                return result

        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name

        if self.invoice_id.pricelist_id and self.invoice_id.partner_id:
            vals['price_unit'] = self._get_display_price(product)
            vals['price_unit_show'] = vals['price_unit']
            print(vals)
            print(vals)
        self.update(vals)
        return result

    @api.model
    def create(self, vals):
        if 'price_unit_show' in vals.keys():
            vals['price_unit'] = vals['price_unit_show']
        res = super(EasyInvoiceLine, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        if 'price_unit_show' in vals.keys():
            vals['price_unit'] = vals['price_unit_show']
        res = super(EasyInvoiceLine, self).write(vals)
        return res
