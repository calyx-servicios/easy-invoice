# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from ast import literal_eval


class StockMove(models.Model):
    _inherit = "stock.move"

    analytic_line_id = fields.Many2one(
        "account.analytic.line", "Analytic Line Move"
    )

    is_in_inventory_adjustment = fields.Boolean(
        "Inventory Adjustment In", default=False
    )

    def _prepare_account_move_line(
        self, qty, cost, credit_account_id, debit_account_id
    ):
        ICPSudo = self.env["ir.config_parameter"].sudo()
        res = super(StockMove, self)._prepare_account_move_line(
            qty, cost, credit_account_id, debit_account_id
        )
        cmv_analytic_account_id = literal_eval(
            ICPSudo.get_param(
                "easy_invoice_income_statements.cmv_analytic_account_id",
                default="False",
            )
        )
        cmv_category_id = literal_eval(
            ICPSudo.get_param(
                "easy_invoice_income_statements.category_commodities",
                default="False",
            )
        )
        cmv_account_id = False

        if cmv_category_id:
            category = self.env["product.category"].browse(
                cmv_category_id
            )
            cmv_account_id = (
                category.property_stock_account_output_categ_id.id
            )
        if cmv_account_id and cmv_analytic_account_id:
            if self._is_out():
                res[0][2][
                    "analytic_account_id"
                ] = cmv_analytic_account_id
            if self.is_in_inventory_adjustment and self._is_in():
                # TO MAKE THE ACCOUNT ENTRY IN INVENTORY ADJUSMENT
                res[1][2][
                    "analytic_account_id"
                ] = cmv_analytic_account_id
        return res
