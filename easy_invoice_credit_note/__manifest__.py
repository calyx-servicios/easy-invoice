# -*- coding: utf-8 -*-
{
    'name': "Easy Invoice Credit Note Report",
    'summary': """
        Easy Invoice customer credit note xlsx report """,
    'author': 'Calyx Servicios S.A.',
    "maintainers": ["ParadisoCristian"],
    'website': 'http://www.calyxservicios.com.ar',
    'category': 'Easy Invoice',
    "license": "AGPL-3",
    'version': '11.0.1.0.0',
    'depends' : [
        'easy_invoice',
        'report_xlsx',
        'easy_invoice_cn_types',
        ],
    'data': [
        'wizard/credit_note_report_wizard_view.xml',
        'report/customer_credit_note_report.xml',
    ],
}
