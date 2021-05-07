# -*- coding: utf-8 -*-
{
    'name': "Easy Invoice Customer Invoice Report",
    'summary': """
        Easy Invoice customer invoice xlsx report """,
    'author': 'Calyx Servicios S.A.',
    "maintainers": ["ParadisoCristian"],
    'website': 'http://www.calyxservicios.com.ar',
    'category': 'Easy Invoice',
    "license": "AGPL-3",
    'version': '11.0.1.0.0',
    'depends' : [
        'easy_invoice',
        'report_xlsx',
        ],
    'data': [
        'wizard/invoice_report_wizard_view.xml',
        'report/customer_invoice_report.xml',
    ],
}
