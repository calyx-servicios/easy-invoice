# -*- coding: utf-8 -*-
{
    'name': "Easy Invoice Cash Register",
    'summary': """
        Mecanismo simple de arque de cajas easy y diarios contables """,

    'description': """
        
    """,
    'author': "Calyx",
    'website': "http://www.calyxservicios.com.ar",
    'category': 'Easy Invoice',
    'version': '11.0.1.0.0',
    'depends' : [
        'account', 
        'easy_invoice',
        'easy_invoice_recaudation',
        ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/cash_register_view.xml',
    ],
}