# -*- coding: utf-8 -*-
{
    "name": "Easy Invoice Account Analytic Relation",
    "summary": """
        Mecanismo simple de Account Analytic para Easy Invoice """,
    "description": """
        
    """,
    "author": "Calyx",
    "website": "http://www.calyxservicios.com.ar",
    "category": "Easy Invoice",
    "version": "11.0.1.1.0",
    "depends": [
        "base",
        "easy_invoice",
        "easy_invoice_income_statements",
        "easy_invoice_partner_cc",
        "easy_invoice_employee_expense",
        "easy_invoice_employee_cc",
        "easy_invoice_sale",
        "account_analytic_sale_in_line",
    ],
    "data": [
        "views/easy_employee_expense_view.xml",
        "views/easy_invoice_view.xml",
        "views/hr_employee_view.xml",
        "views/product_category_view.xml",
    ],
}
