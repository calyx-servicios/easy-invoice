# -*- coding: utf-8 -*-
{
    'name': "Easy Invoice Analysis Unit Detail",
    'summary': """
        Adds a column to the invoice line analysis report tree view""",

    'description': """

    """,
    'author': "Calyx",
    'website': "http://www.calyxservicios.com.ar",
    'category': 'Easy Invoice',
    'version': '11.0.1.0.0',
    'depends' : [
        'easy_invoice',
        'easy_invoice_analysis',
        'hr',
        'base',
        'report_xlsx',
        'account_financial_report',
        'account',
        'l10n_ar_account',
        ],
    'data': [
        'views/analysis_report_line_view.xml'
    ],
}