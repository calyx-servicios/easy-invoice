# -*- coding: utf-8 -*-
# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, exceptions, fields, models, _
from odoo.tools import float_is_zero, float_compare, pycompat
from odoo.tools.misc import formatLang

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class CostCenterMove(models.Model):
    _inherit = "cost.center.move"
  
### posible metodo para ontrlar el estado depseus de ver bienc omo deberia funcionar
    # @api.depends('invoice_id.price_subtotal', 'currency_id', 'company_id', 'date_invoice', 'type')
    # def _compute_state(self):
    #     round_curr = self.currency_id.round
    #     self.amount_total = sum(line.price_subtotal for line in self.invoice_line_ids)
    #     sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
    #     self.amount_total_signed = self.amount_total * sign
### posible metodo para ontrlar el estado depseus de ver bienc omo deberia funcionar

#### Fields
    state_easy_invoice = fields.Selection([('open', 'Open'),
                                           ('payed', 'Payed')
                                           ], string='Status', index=True,  default='open',) #compute='_compute_state'
 
    payment_id = fields.Many2one('easy.payment', string='Payment',) #ondelete='cascade'
    invoice_id = fields.Many2one('easy.invoice', string='Invoice',  )
    partner_cc_id = fields.Many2one('easy.partner.cc', string='Partner CC', )
    employee_cc_id = fields.Many2one('easy.employee.cc', string='Employee CC', )
    employee_expense_id = fields.Many2one('easy.employee.expense', string='Employee Expense', )


## fields para tener de borrador
    # name = fields.Char('Description', required=True)

    # state = fields.Selection([('open', 'Open'),
    #                           ('validate', 'Validate')
    #                           ], string='Status', index=True,  default='open',)

    # date = fields.Date('Date', required=True, index=True, default=fields.Date.context_today)
    # amount = fields.Monetary('Amount', required=True, default=0.0)
    # #unit_amount = fields.Float('Quantity', default=0.0)
    # cost_center_id = fields.Many2one('cost.center', 'Cost Center', required=True, ondelete='restrict', index=True)
    # partner_id = fields.Many2one('res.partner', string='Partner')


#### end Fields

