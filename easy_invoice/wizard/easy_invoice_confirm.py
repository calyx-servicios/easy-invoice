# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError


class EasyInvoiceConfirm(models.TransientModel):

    _name = "easy.invoice.confirm"
    _description = "Confirm the selected invoices"

    @api.multi
    def invoice_confirm(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['easy.invoice'].browse(active_ids):
            if record.state != 'draft':
                raise UserError(_("Selected invoice(s) cannot be confirmed as they are not in 'Draft' state."))
            record.confirm()
        return {'type': 'ir.actions.act_window_close'}
