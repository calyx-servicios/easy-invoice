from odoo import api, exceptions, fields, models, _
from odoo.tools import float_is_zero, float_compare, pycompat
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class EasyPaymentGroupLine(models.Model):

    _name = "easy.payment.group.line"
    _description = "Easy Payment Group Line"
    _order = "date_invoice"

### Fields
    invoice_id = fields.Many2one('easy.invoice', string='Invoice')
    payment_id = fields.Many2one('easy.payment', string='Payment')

    residual_amount = fields.Monetary(string='Residual Amount',)#Monetary(related='invoice_id.residual_amount',string='Residual Amount',)
    #history_residual_amount = fields.Monetary(string='Residual Amount',)
    date_invoice = fields.Date(related='invoice_id.date_invoice',string='Date Invoice ',store=True)
    partner_id = fields.Many2one('res.partner',  string="Partner", readonly=False)
    currency_id = fields.Many2one('res.currency',  string="Currency", readonly=False)

    amount2pay = fields.Monetary(string='Amount to Pay', )
    amount2payed = fields.Monetary(string='Amount to Payed', )

    in_invoice_group_id = fields.Many2one('easy.payment.group', string='In Invoice Group')
    in_rectificative_group_id = fields.Many2one('easy.payment.group', string='In Rect Invoice Group')

    out_invoice_group_id = fields.Many2one('easy.payment.group', string='Out Invoice Group')
    out_rectificative_group_id = fields.Many2one('easy.payment.group', string='Out Rect Invoice Group')
  
### ends Field   

    # @api.multi
    # @api.onchange('residual_amount')
    # def onchange_residual_amount(self):
    #     for rec in self:
    #         group_obj = rec.in_invoice_group_id
    #         if not group_obj:
    #             group_obj = rec.in_rectificative_group_id
    #         if not group_obj:
    #             group_obj = rec.out_invoice_group_id
    #         if not group_obj:
    #             group_obj = rec.out_rectificative_group_id
    #         if group_obj and group_obj.state == 'draft':
    #             rec.residual_amount = rec.invoice_id.residual_amount