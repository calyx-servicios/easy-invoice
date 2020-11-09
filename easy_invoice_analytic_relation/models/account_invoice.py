# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def action_invoice_open(self):
        """
            Remove the account analytic entries for supplier invoice
            if the product is in a specific category and if is type
            'product'
        """
        res = super(AccountInvoice, self).action_invoice_open()
        for invoice in self:
            if invoice.type == "in_invoice":
                if invoice.move_id:
                    for line in invoice.move_id.line_ids:
                        if line.analytic_line_ids:
                            for analytic in line.analytic_line_ids:
                                if (
                                    analytic.product_category_id.account_analytic
                                    or analytic.product_category_id.parent_id.account_analytic
                                ):
                                    if (
                                        analytic.product_id.type
                                        == "product"
                                    ):
                                        analytic.unlink()
                                        continue
        return res
