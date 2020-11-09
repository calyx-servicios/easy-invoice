from odoo import models, api, fields, _
from ast import literal_eval
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import logging

_logger = logging.getLogger(__name__)


class EasyRecaudationCloseBill(models.TransientModel):
    _name = 'easy.recaudation.close.bill'

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id

    close_id = fields.Many2one('easy.recaudation.close', string='Recaudation')
    bill_id = fields.Many2one('easy.bill', string='Bill')
    quantity = fields.Integer(string='Quantity',default=0)
    amount = fields.Monetary(string='Amount',readonly=True)
    
    currency_id = fields.Many2one('res.currency', string='Currency',
        required=True, readonly=True, default=_default_currency)

    @api.onchange('quantity')
    def _compute_amount(self):
        amount=0.0
        for line in self:
            line.amount = line.bill_id.value * line.quantity

class EasyRecaudationClose(models.TransientModel):

    _name = 'easy.recaudation.close'
    _description = 'Easy Recaudation Close'

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id
    
    @api.model
    def _default_amount_box(self):
        recaudation = self.env['easy.recaudation'].browse(self._context.get('active_id'))
        return recaudation.amount_box


    amount = fields.Monetary(string='Amount')
    currency_id = fields.Many2one('res.currency', string='Currency',
        required=True, readonly=True, default=_default_currency)
    amount_box = fields.Monetary(string='Amount Box',readonly=True, default=_default_amount_box)
    amount_difference = fields.Monetary(string='Amount Difference',readonly=True)
    reason = fields.Char(string='Amount Difference Reason',help='Enter the reason of the amount difference')

    @api.model
    def _default_bills(self):
        bill_ids = self.env['easy.bill'].search([])
        lines = []
        for bill in self.env['easy.bill'].browse(bill_ids):
            lines.append({'bill_id':bill.id,'quantity':0.0})
        return lines

    bill_ids = fields.One2many('easy.recaudation.close.bill', 'close_id', string='Bill',default=_default_bills)

    @api.onchange('bill_ids')
    def _compute_amount(self):
        _logger.info('======compute line amounts====== %r ',self)
        for close in self:
            for line in close.bill_ids:
                amount = amount + line.bill_id.value * line.quantity
            close.amount=amount
            close.amount_difference=close.amount-close.amount_box

    @api.onchange('amount')
    def _compute_amount(self):
        for close in self:
            close.amount_difference=close.amount-close.amount_box

    @api.multi
    def partial_close(self):
        for close in self: 
            difference=close.amount-close.amount_box
            if difference!=0 and (close.reason == '' or not close.reason):
                close.amount_difference=difference
                raise Warning(_("There is a amount difference and no reason especified : %s" % difference))
            recaudation = self.env['easy.recaudation'].browse(self._context.get('active_id'))
            _logger.info('Recaudation Close: %r ',recaudation.id)
            _logger.info('Recaudation Close Difference: %r ',close.amount_difference)
            _logger.info('Recaudation Close Amount: %r ',close.amount)
            _logger.info('Recaudation Close Amount Box: %r ',close.amount_box)
            for bill in close.bill_ids:
                _logger.info('Recaudation Close Bill: %r ',bill.bill_id.value)
            recaudation.partial_close(close.amount-close.amount_box,close.reason)