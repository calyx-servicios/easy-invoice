# -*- coding: utf-8 -*-
{
    'name': "Easy Invoice Employee CC Import",
    'summary': """
        Mecanismo simple de importación movimientos de cuenta de Empleados""",
    'description': """
        
    """,
    'author': "Calyx",
    'website': "http://www.calyxservicios.com.ar",
    'category': 'Easy Invoice',
    'version': '11.0.1.0.0',
    'depends' : [
        #'base', 
        'easy_invoice_employee_cc',
        ],
    'data': [
        'security/ir.model.access.csv',
        'views/easy_employee_cc_import_view.xml',
        #'views/hr_employee_view.xml',

    ],
    'external_dependencies': {
        'python': ['openpyxl',],
    },
}