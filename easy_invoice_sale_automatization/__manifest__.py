# -*- coding: utf-8 -*-
{
    'name': "Easy Invoice Sale Automatization",
    'summary': """
        Modulo encargado de automatizar la creación de Facturas Easy desde las ordenes de Ventas""",

    'description': """
        
    """,
    'author': "Calyx",
    'website': "http://www.calyxservicios.com.ar",
    'category': 'Customs',
    'version': '11.0.1.0.0',
    'depends' : [
        'easy_invoice_sale',
        'sale',
        ],
    'data': [
        'wizards/sale_order_invoice_confirm_view.xml',
        'views/sale_order_view.xml',
    ],
}