# -*- coding: utf-8 -*-
{
    'name': "Easy Invoice Cost Center Relation",
    'summary': """
        Mecanismo simple de Centro de Costo para Easy Invoice """,

    'description': """
        
    """,
    'author': "Calyx",
    'website': "http://www.calyxservicios.com.ar",
    'category': 'Easy Invoice',
    'version': '11.0.1.0.0',
    'depends' : [
        'base', 
        'easy_invoice',
        #'easy_invoice_recaudation',
        'easy_invoice_partner_cc',
        'easy_invoice_employee_expense',
        'easy_invoice_employee_cc',
        'easy_invoice_sale',
        'cost_center',
        ],
    'data': [

        'wizard/wizard_edit_cost_center_view.xml',
        
        'views/easy_invoice_view.xml',
        'views/hr_employee_view.xml',
        'views/sale_order_view.xml',
        'views/easy_employee_expense_view.xml',


        
    ],
}