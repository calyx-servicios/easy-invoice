# -*- coding: utf-8 -*-
{
    'name': "Easy Invoice List and List of lines",
    'summary': """
        Simple view of Invoice and Invoice Lines """,
    'description': """
        
    """,
    'author': "Calyx",
    'website': "http://www.calyxservicios.com.ar",
    'category': 'Easy Invoice',
    'version': '11.0.1.0.0',
    'depends' : [
        #'base', 
        'easy_invoice',
        'easy_invoice_partner_cc',
        ],
    'data': [
        'views/easy_invoice_view.xml',
        'views/easy_invoice_line_view.xml',
    ],
}