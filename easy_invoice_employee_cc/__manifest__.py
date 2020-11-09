# -*- coding: utf-8 -*-
{
    "name": "Easy Invoice Employee CC",
    "summary": """
        Mecanismo simple de Gestión de Cuentas Corrientes y Pagos a Empleados """,
    "description": """
        
    """,
    "author": "Calyx",
    "website": "http://www.calyxservicios.com.ar",
    "category": "Easy Invoice",
    "version": "11.0.1.0.0",
    "depends": ["base", "hr", "easy_invoice", "easy_invoice_recaudation",],
    "data": [
        "wizard/wizard_easy_employee_cc_conf_view.xml",
        "wizard/wizard_easy_employee_cc_create_view.xml",
        "report/print_salary_advancement_view.xml",
        "report/invoice_employee_report_template.xml",
        "security/ir.model.access.csv",
        "views/hr_employee_view.xml",
        "data/easy_employee_cc_settlement.xml",
    ],
}
