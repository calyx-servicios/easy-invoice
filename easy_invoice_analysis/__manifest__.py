# -*- coding: utf-8 -*-
{
    'name': "Easy Invoice Analysis",
    'summary': """
        Easy Invoice Analysis""",

    'description': """

    """,
    'author': "Calyx",
    'website': "http://www.calyxservicios.com.ar",
    'category': 'Easy Invoice',
    'version': '11.0.1.2.0',
    'depends' : [
        'easy_invoice',
        'hr',
        'base',
        'report_xlsx',
        'account_financial_report',
        'account',
        'l10n_ar_account',
        ],
    'data': [
        "security/ir.model.access.csv",
        'views/analysis_report_line_view.xml'
    ],
}
