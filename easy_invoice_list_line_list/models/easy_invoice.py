from odoo import models, api, fields


class EasyInvoiceLine(models.Model):

    _inherit = "easy.invoice"

    amount_total_signed = fields.Float(string="Total", compute="_compute_amount_total_signed", store=True)

    @api.depends('amount_total', 'type')
    def _compute_amount_total_signed(self):
        for invoice in self:
            if invoice.type == 'out_refund':
                invoice.amount_total_signed = -invoice.amount_total
            else:
                invoice.amount_total_signed = invoice.amount_total
