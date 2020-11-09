# -*- coding: utf-8 -*-
{
    'name': "Easy Invoice Partner CC",
    'summary': """
        Mecanismo simple facturacion rapida Con Cuentas de Proveedores/Cliente """,
    'description': """
        
    """,
    'author': "Calyx",
    'website': "http://www.calyxservicios.com.ar",
    'category': 'Easy Invoice',
    'version': '11.0.1.0.0',
    'depends' : [
        #'base', 
        'easy_invoice',
        'easy_invoice_recaudation',
        ],
    'data': [
        'report/print_anticipe_advancement_view.xml',
        'security/ir.model.access.csv',
        
        'views/menu_view.xml',
        'views/res_partner_view.xml',
        'views/easy_payment_group_view.xml',
        'views/easy_partner_cc_view.xml',

        'wizard/wizard_easy_partner_cc_view.xml',
    ],
}