# -*- coding: utf-8 -*-
{
    'name': "Easy Invoice Purchase",
    'summary': """
        Mecanismo simple facturacion rapida Con Purchase """,

    'description': """
        
    """,
    'author': "Calyx",
    'website': "http://www.calyxservicios.com.ar",
    'category': 'Easy Invoice',
    'version': '11.0.1.0.0',
    'depends' : [
        'base', 
        'easy_invoice',
        'purchase',
        ],
    'data': [
        'views/easy_invoice_view.xml',
        'views/purchase_order_view.xml',
    ],
}