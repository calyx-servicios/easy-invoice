# -*- coding: utf-8 -*-
{
    "name": "Easy Invoice Income Statements",
    "summary": """
        Income Statements Integrated with Easy Invoice """,
    "description": """

    """,
    "author": "Calyx",
    "website": "http://www.calyxservicios.com.ar",
    "category": "Easy Invoice",
    "version": "11.0.1.1.0",
    "depends": [
        "easy_invoice",
        "base",
        "report_xlsx",
        "account_financial_report",
        "stock_account",
        "analytic_product_category",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/income_statements_wizard_view.xml",
        "views/base_menu_view.xml",
        "views/res_config_settings_views.xml",
        "views/product_view.xml",
        "views/stock_account_views.xml",
        "report/template/layouts.xml",
        "report/template/income_statements.xml",
        "reports.xml",
    ],
}
