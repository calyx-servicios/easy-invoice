# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class EasyInvoice(models.Model):
    _inherit = "easy.invoice"

    @api.multi
    def create_line_residual(self):
        var_return = super(EasyInvoice, self).create_line_residual()
        for rec in self:
            for line_obj in rec.invoice_line_ids:
                if rec.type == "in_invoice":
                    if (
                        line_obj.product_id.categ_id.account_analytic
                        or line_obj.product_id.categ_id.parent_id.account_analytic
                    ):
                        if line_obj.product_id.type == "product":
                            continue
                        else:
                            line_obj.create_line_analytic_account_line()
                    else:
                        line_obj.create_line_analytic_account_line()
                else:
                    line_obj.create_line_analytic_account_line()

        return var_return

    @api.multi
    def cancel_invoice(self):
        var_return = super(EasyInvoice, self).cancel_invoice()
        for self_obj in self:
            for line_obj in self_obj.invoice_line_ids:
                if line_obj.analytic_line_id:
                    line_obj.analytic_line_id.unlink()
        return var_return
