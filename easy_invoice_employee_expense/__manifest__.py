# -*- coding: utf-8 -*-
{
    'name': "Easy Invoice Employee Expense",
    'summary': """
        Mecanismo simple de Gestión de Gastos de Empleados""",
    'description': """
        
    """,
    'author': "Calyx",
    'website': "http://www.calyxservicios.com.ar",
    'category': 'Easy Invoice',
    'version': '11.0.1.0.0',
    'depends' : [
        'base', 
        'easy_invoice', 
        'easy_invoice_employee_cc',
        'easy_invoice_recaudation',
        ],
    'data': [
        'security/ir.model.access.csv',
        'views/easy_employee_expense_view.xml',
        'views/hr_employee_view.xml',
        'views/easy_invoice_view.xml',

    ],
}