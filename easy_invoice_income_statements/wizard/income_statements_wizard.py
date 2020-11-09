# Copyright 2016 Camptocamp SA
# Copyright 2017 Akretion - Alexis de Lattre
# Copyright 2018 Eficent Business and IT Consuting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.tools import pycompat
from odoo.exceptions import UserError, ValidationError


class IncomeStatementsReportWizard(models.TransientModel):
    """Income Statements Report Wizard."""

    _name = "income.statements.report.wizard"
    _description = "Income Statements Report Wizard."

    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.user.company_id,
        required=False,
        string="Company",
    )
    company_ids = fields.Many2many(
        comodel_name="res.company", string="Filter Companies",
    )
    date_range_id = fields.Many2one(
        comodel_name="date.range", string="Date range"
    )
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)

    account_ids = fields.Many2many(
        comodel_name="account.analytic.account",
        string="Filter Accounts",
    )

    category_ids = fields.Many2many(
        comodel_name="product.category", string="Filter Category",
    )

    product_ids = fields.Many2many(
        comodel_name="product.product", string="Filter Product",
    )

    by_category = fields.Boolean(string="By Category", default=True)
    by_month = fields.Boolean("Split by Month")

    @api.onchange("date_range_id")
    def onchange_date_range_id(self):
        """Handle date range change."""
        self.date_from = self.date_range_id.date_start
        self.date_to = self.date_range_id.date_end

    @api.multi
    def button_export_html(self):
        self.ensure_one()
        action = self.env.ref(
            "easy_invoice_income_statements.action_report_income_statements"
        )
        vals = action.read()[0]
        context1 = vals.get("context", {})
        if isinstance(context1, pycompat.string_types):
            context1 = safe_eval(context1)
        model = self.env["report_income_statements"]
        report = model.create(self._prepare_report_income_statements())
        report.compute_data_for_report()

        context1["active_id"] = report.id
        context1["active_ids"] = report.ids
        vals["context"] = context1
        return vals

    @api.multi
    def button_export_pdf(self):
        self.ensure_one()
        report_type = "qweb-pdf"
        return self._export(report_type)

    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        action = self.env.ref(
            "easy_invoice_income_statements.action_report_income_statements_xlsx"
        )
        vals = action.read()[0]
        context1 = vals.get("context", {})
        if isinstance(context1, pycompat.string_types):
            context1 = safe_eval(context1)
        model = self.env["report_income_statements"]
        report = model.create(self._prepare_report_income_statements())
        report.compute_data_for_report()

        context1["active_id"] = report.id
        context1["active_ids"] = report.ids
        vals["context"] = context1
        return vals

    def _prepare_report_income_statements(self):
        self.ensure_one()
        return {
            "date_from": self.date_from,
            "date_to": self.date_to,
            "company_id": self.company_id.id,
            "filter_account_ids": [(6, 0, self.account_ids.ids)],
            "filter_category_ids": [(6, 0, self.category_ids.ids)],
            "filter_product_ids": [(6, 0, self.product_ids.ids)],
            "filter_company_ids": [(6, 0, self.company_ids.ids)],
            "show_lines": not self.by_category,
            "by_month": self.by_month,
        }

    def _export(self, report_type):
        """Default export is PDF."""
        model = self.env["report_income_statements"]
        report = model.create(self._prepare_report_income_statements())
        report.compute_data_for_report()
        return report.print_report(report_type)
