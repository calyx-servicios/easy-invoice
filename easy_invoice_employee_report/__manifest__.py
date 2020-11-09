# -*- coding: utf-8 -*-
{
    'name': "Easy Invoice Employee Report",
    'summary': """
        Easy Invoice Employee Report """,

    'description': """

    """,
    'author': "Calyx",
    'website': "http://www.calyxservicios.com.ar",
    'category': 'Easy Invoice',
    'version': '11.0.1.0.0',
    'depends' : [
        'easy_invoice',
        'hr',
        'easy_invoice_employee_cc',
        'base',
        'report_xlsx',
        'account_financial_report',
        ],
    'data': [
        "security/ir.model.access.csv",
        'wizard/employee_report_wizard_view.xml',
        'report/template/layouts.xml',
        'report/template/employee_report.xml',
        'reports.xml',
    ],
}
