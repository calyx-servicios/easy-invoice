# -*- coding: utf-8 -*-
{
    'name': "Easy Invoice Sale",
    'summary': """
        Mecanismo simple facturacion rapida """,

    'description': """

    """,
    'author': "Calyx",
    'website': "http://www.calyxservicios.com.ar",
    'category': 'Easy Invoice',
    'version': '11.0.1.0.0',
    'depends' : [
        'base',
        'easy_invoice',
        'sale',
        'sale_management',
        ],
    'data': [
        'security/ir.model.access.csv',
        'views/easy_invoice_view.xml',
        'views/sale_order_view.xml',
    ],
}
