# -*- coding: utf-8 -*-
{
    "name": "Easy Invoice Recaudation",
    "summary": """
        Mecanismo simple facturacion rapida """,
    "description": """
        
    """,
    "author": "Calyx",
    "website": "http://www.calyxservicios.com.ar",
    "category": "Easy Invoice",
    "version": "11.0.1.0.0",
    "depends": ["base_setup", "base", "easy_invoice"],
    "data": [
        "security/ir.model.access.csv",
        # 'report/payment_template.xml',
        # 'report/payment_group_template.xml',
        "wizard/easy_invoice_payment_view.xml",
        "wizard/easy_recaudation_close_view.xml",
        "wizard/easy_recaudation_retire_deposit_view.xml",
        "views/base_menu_view.xml",
        "views/easy_recaudation_view.xml",
        "views/easy_invoice_view.xml",
        "views/easy_payment_group_view.xml",
        "views/easy_sequence_view.xml",
        "views/easy_bill_view.xml",
    ],
}
