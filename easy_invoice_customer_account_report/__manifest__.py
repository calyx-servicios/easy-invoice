# -*- coding: utf-8 -*-
{
    'name': "Easy Invoice Customer Account Report",
    'summary': """
        Easy Invoice Customer Account Report """,

    'description': """

    """,
    'author': "Calyx",
    'website': "http://www.calyxservicios.com.ar",
    'category': 'Easy Invoice',
    'version': '11.0.1.0.0',
    'depends' : [
        'easy_invoice',
        'easy_invoice_partner_cc',
        'base',
        'report_xlsx',
        'account_financial_report',
        ],
    'data': [
        'wizard/customer_account_report_wizard_view.xml',
        'views/base_menu_view.xml',
        'report/template/layouts.xml',
        'report/template/customer_account_report.xml',
        'reports.xml',
    ],
}
