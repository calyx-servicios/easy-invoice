# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from ast import literal_eval

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    category_sales=fields.Many2one('product.category', string='Sales Category', domain=[('parent_id', '=', False)])
    category_commodities=fields.Many2one('product.category', string='Commodities Category', domain=[('parent_id', '=', False)])
    category_gross_profit=fields.Many2one('product.category', string='Gross Profit Category', domain=[('parent_id', '=', False)])
    category_gross_profit_percentage=fields.Many2one('product.category', string='Gross Profit Category [%]', domain=[('parent_id', '=', False)])
    category_expenses=fields.Many2one('product.category', string='Expenses Total', domain=[('parent_id', '=', False)])
    category_net_profit=fields.Many2one('product.category', string='Net Profit Category', domain=[('parent_id', '=', False)])
    category_net_profit_percentage=fields.Many2one('product.category', string='Net Profit Category [%]', domain=[('parent_id', '=', False)])
    category_expense_ids= fields.Many2many(comodel_name='product.category',string='Expense Categories',)
    cmv_analytic_account_id=fields.Many2one('account.analytic.account', string='CMV Analytic Account',)
    create_account_move = fields.Boolean("Creates Account Move", default=False)

    def get_category(self, name):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        category_name="""easy_invoice_income_statements."""
        category_name+=name
        category_id = literal_eval(ICPSudo.get_param(category_name, default='False'))
        if category_id and not self.env['product.category'].browse(category_id).exists():
            category_id = False
        return category_id

    @api.model
    def get_values(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res = super(ResConfigSettings, self).get_values()
        category_sales_id = self.get_category('category_sales')
        category_commodities_id = self.get_category('category_commodities')
        category_gross_profit_id = self.get_category('category_gross_profit')
        category_gross_profit_percentage_id = self.get_category('category_gross_profit_percentage')
        category_expenses_id = self.get_category('category_expenses')
        category_net_profit_id = self.get_category('category_net_profit')
        category_net_profit_percentage_id = self.get_category('category_net_profit_percentage')
        category_expense_ids = literal_eval(ICPSudo.get_param('easy_invoice_income_statements.category_expense_ids', default='False'))
        cmv_analytic_account_id = literal_eval(ICPSudo.get_param('easy_invoice_income_statements.cmv_analytic_account_id', default='False'))
        res.update(
            category_sales=category_sales_id,
            category_commodities=category_commodities_id,
            category_gross_profit=category_gross_profit_id,
            category_gross_profit_percentage=category_gross_profit_percentage_id,
            category_expenses=category_expenses_id,
            category_net_profit=category_net_profit_id,
            category_net_profit_percentage=category_net_profit_percentage_id,
            category_expense_ids=category_expense_ids,
            cmv_analytic_account_id=cmv_analytic_account_id
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("easy_invoice_income_statements.category_sales", self.category_sales.id)
        ICPSudo.set_param("easy_invoice_income_statements.category_commodities", self.category_commodities.id)
        ICPSudo.set_param("easy_invoice_income_statements.category_gross_profit", self.category_gross_profit.id)
        ICPSudo.set_param("easy_invoice_income_statements.category_gross_profit_percentage", self.category_gross_profit_percentage.id)
        ICPSudo.set_param("easy_invoice_income_statements.category_expenses", self.category_expenses.id)
        ICPSudo.set_param("easy_invoice_income_statements.category_net_profit", self.category_net_profit.id)
        ICPSudo.set_param("easy_invoice_income_statements.category_net_profit_percentage", self.category_net_profit_percentage.id)
        ICPSudo.set_param("easy_invoice_income_statements.category_expense_ids", self.category_expense_ids.ids)
        ICPSudo.set_param("easy_invoice_income_statements.cmv_analytic_account_id", self.cmv_analytic_account_id.id)
        self._set_auto_sequence()

    @api.multi
    def _set_auto_sequence(self):
        if self.category_sales:
            self.category_sales.sequence=1
        if self.category_commodities:
            self.category_commodities.sequence=2
        if self.category_gross_profit:
            self.category_gross_profit.sequence=3
        if self.category_gross_profit_percentage:
            self.category_gross_profit_percentage.sequence=4
        if self.category_expenses.sequence:
            self.category_expenses.sequence=5
        if self.category_net_profit.sequence:
            self.category_net_profit.sequence=6
        if self.category_net_profit_percentage:
            self.category_net_profit_percentage.sequence=7
