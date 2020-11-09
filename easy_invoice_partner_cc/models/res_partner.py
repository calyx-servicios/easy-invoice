# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _

class ResPartner(models.Model):
    _inherit = "res.partner"



### Fields
    cc_line_ids = fields.One2many('easy.partner.cc', 'partner_id', string='Anticipe/Advancement')

    open_easy_invoice_ids = fields.One2many('easy.invoice', 'partner_id', string='Easy Invoice',
        domain=[('state', '=', 'open')])
    open_invoice_ids = fields.One2many('account.invoice', 'partner_id', string='Invoice', readonly=True,
        domain=[('state', '=', 'open')])
    
    amount_anticipe = fields.Monetary(string='Anticipe',readonly=True, compute='_control_total_amount')
    amount_advancement = fields.Monetary(string='Advancement',readonly=True, compute='_control_total_amount')

    total_amount_debit = fields.Monetary(string='Debit',readonly=True, compute='_control_total_amount')
    total_amount_credit = fields.Monetary(string='Credit',readonly=True, compute='_control_total_amount')
    account_amount_debit = fields.Monetary(string='Debit',readonly=True, compute='_control_total_amount')
    account_amount_credit = fields.Monetary(string='Credit',readonly=True, compute='_control_total_amount')
    easy_amount_debit = fields.Monetary(string='Debit',readonly=True, compute='_control_total_amount')
    easy_amount_credit = fields.Monetary(string='Credit',readonly=True, compute='_control_total_amount')
    easy_amount_balance = fields.Monetary(string='Balance',readonly=True, compute='_control_total_amount')
    amount_balance = fields.Monetary(string='Odoo Balance',readonly=True, compute='_control_total_amount')
    total_amount_balance = fields.Monetary(string='Total Balance',readonly=True, compute='_control_total_amount')
### end Fields

    
    @api.multi
    @api.depends('cc_line_ids.amount_anticipe', 
                 'cc_line_ids.amount_advancement',
                 'open_easy_invoice_ids.residual_amount',
                 'open_invoice_ids.residual')
    def _control_total_amount(self):
        for rec in self:
            total_amount_debit  = 0.0
            total_amount_credit   = 0.0

            ### Anticipos y Adelantos
            amount_anticipe = 0.0
            amount_advancement = 0.0
            for line_obj in rec.cc_line_ids:
                if line_obj.state != 'cancel':
                    amount_anticipe += line_obj.amount_anticipe 
                    amount_advancement += line_obj.amount_advancement 
            rec.amount_anticipe = amount_anticipe
            rec.amount_advancement = amount_advancement
            total_amount_credit +=  amount_anticipe
            total_amount_debit += amount_advancement

            ### Facturas Easy
            easy_amount_debit   = 0.0
            easy_amount_credit   = 0.0 


            for invoice_obj in rec.open_easy_invoice_ids:

                if invoice_obj.type in ('out_invoice'):
                    easy_amount_debit += invoice_obj.residual_amount
                if invoice_obj.type in ('out_refund'):
                    easy_amount_credit += invoice_obj.residual_amount

                if invoice_obj.type in ('in_invoice'):
                    easy_amount_credit += invoice_obj.residual_amount
                if invoice_obj.type in ('in_refund'):
                    easy_amount_debit  += invoice_obj.residual_amount
                   
            rec.easy_amount_debit = easy_amount_debit
            rec.easy_amount_credit = easy_amount_credit
            total_amount_debit += easy_amount_debit
            total_amount_credit +=  easy_amount_credit
            rec.easy_amount_balance = total_amount_debit - total_amount_credit
            ### Facturas Account Invoice
            account_amount_debit   = 0.0
            account_amount_credit   = 0.0

            ## si aca no esta bien los tipos tendria que arreglarse abajo
            for invoice_obj in rec.open_invoice_ids:
                if invoice_obj.type in ('out_invoice','in_refund'):
                    account_amount_debit += invoice_obj.residual
                if invoice_obj.type in ('in_invoice','out_refund'):
                    account_amount_credit += invoice_obj.residual
            ####  aca hace las cuentas como lo de arriba de easy invoice   

            rec.account_amount_debit = account_amount_debit
            rec.account_amount_credit = account_amount_credit
            rec.amount_balance = account_amount_debit - account_amount_credit
            rec.total_amount_balance = rec.easy_amount_balance + rec.amount_balance
            total_amount_debit += account_amount_debit
            total_amount_credit +=  account_amount_credit

            #### control de las sumas final
            if total_amount_debit > total_amount_credit:
                rec.total_amount_debit = total_amount_debit -total_amount_credit
                rec.total_amount_credit = 0.0
            else:
                rec.total_amount_debit =  0.0
                rec.total_amount_credit = total_amount_credit-total_amount_debit
