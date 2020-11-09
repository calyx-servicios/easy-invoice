# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _


class EasyInvoice(models.Model):

    _inherit = "easy.invoice"
    pricelist_id = fields.Many2one('product.pricelist',
                                   string='Pricelist',
                                   required=True,
                                   readonly=True,
                                   states={
                                       'draft': [('readonly', False)],
                                       'sent': [('readonly', False)]},
                                   help="Pricelist for current Easy Invoices.")

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        values = {
            'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
            'user_id': self.partner_id.user_id.id or self.env.uid
        }
        self.update(values)
