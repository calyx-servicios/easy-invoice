# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _

class EasyInvoiceLine(models.Model):
    
    _inherit = "easy.invoice.line"


    invoice_type = fields.Selection(string='Invoice Type',
        related='invoice_id.type',)
    partner_id = fields.Many2one('res.partner', string='Partner',
        related='invoice_id.partner_id', store=True, readonly=True, related_sudo=False)
    date_invoice = fields.Date( string='Date Invoice',
        related='invoice_id.date_invoice', store=True, readonly=True, related_sudo=False)