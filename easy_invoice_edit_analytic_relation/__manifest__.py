# -*- coding: utf-8 -*-
{
    'name': "Easy Invoice Edit Account Analytic",
    'summary': """
        Mecanismo simple para Editar Account Analytic para Easy Invoice """,

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
        'easy_invoice_analytic_relation',
        ],
    'data': [
        
        'wizard/wizard_edit_analytic_account_view.xml',
        'views/easy_employee_expense_view.xml',
        'views/easy_invoice_view.xml',
        'views/hr_employee_view.xml',


        
    ],
}