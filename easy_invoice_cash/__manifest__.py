# pylint: disable=missing-module-docstring,pointless-statement
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Easy Invoice CashBox",
    "summary": """
        Generate an additional tab within the easy boxes that allows to bring the movements of the cash diaries that one configures in said tab,
        which are tag type and are updated automatically.And the totals of that tab are shown and there are other fields with the totals.
        Including the posibility to print a xlsx report.
    """,
    "author": "Calyx Servicios S.A.",
    "maintainers": ["ParadisoCristian"],
    "website": "https://odoo.calyx-cloud.com.ar/",
    "license": "AGPL-3",
    "category": "EasyInvoice",
    "version": "11.0.3.0.0",
    "application": False,
    "installable": True,
    "depends": ["easy_invoice_recaudation"],
    'data': [
        'views/easy_recaudation_views.xml',
        'views/easy_recaudation_xlsx_views.xml',
    ],
}
