# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _


class EasyInvoiceLine(models.Model):
    _inherit = "easy.invoice.line"

    analytic_account_id = fields.Many2one(
        "account.analytic.account", "Analytic Account"
    )
    analytic_line_id = fields.Many2one(
        "account.analytic.line", "Analytic Line Move"
    )

    @api.multi
    def create_line_residual(self):
        var_return = super(EasyInvoiceLine, self).create_line_residual()
        self.create_line_analytic_account_line()
        return var_return

    @api.multi
    def create_line_analytic_account_line(self, analytic=None):
        for rec in self:
            sign = -1.0

            if (
                rec.invoice_id.type in ("out_invoice")
                and rec.invoice_id.subtype_invoice == "invoice"
            ):
                sign = 1.0
            if (
                rec.invoice_id.type in ("in_invoice")
                and rec.invoice_id.subtype_invoice == "debit_note"
            ):
                sign = 1.0
            if rec.invoice_id.type in ("in_refund"):
                sign = 1.0

            analytic_account_obj = rec.analytic_account_id
            if analytic:
                analytic_account_obj = analytic
                rec.analytic_account_id = analytic_account_obj.id

            if analytic_account_obj:
                amount2use = rec.price_subtotal
                vals = {
                    "name": rec.product_id.name,
                    "product_id": rec.product_id.id,
                    "account_id": analytic_account_obj.id,
                    "unit_amount": 1,
                    "date": rec.invoice_id.date_contable,
                    "invoice_line_id": rec.id,
                    "amount": amount2use * sign,
                }
                line_created = self.env["account.analytic.line"].create(
                    vals
                )
                rec.analytic_line_id = line_created.id

    @api.multi
    def create_message(self, old):
        self.ensure_one()
        subject = _("Se crea Movimiento Analítico")
        message = _("Se creacon la cuenta Cuenta Analítica ") + _(
            old.name
        )
        message += _(" en la linea ") + _(self.name)
        user_ids = self.env["res.users"].search([("active", "=", True)])
        self.env["mail.message"].create(
            {
                "message_type": "notification",
                "body": message,
                "subject": subject,
                "needaction_partner_ids": [
                    (4, user.partner_id.id, None) for user in user_ids
                ],
                "model": "easy.invoice",
                "res_id": self.invoice_id.id,
            }
        )
