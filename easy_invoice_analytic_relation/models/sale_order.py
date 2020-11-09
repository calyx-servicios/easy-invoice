# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
            


    @api.multi
    def _prepare_line_easy_invoice(self, invoice_created):
        res = super(SaleOrderLine, self)._prepare_line_easy_invoice(invoice_created)
        if self.product_id and self.product_id.product_tmpl_id.analytic_id:
            res['analytic_account_id']= self.product_id.product_tmpl_id.analytic_id.id
        _logger.debug('_prepare_easy_invoice_line %s' , res)
        return res
          