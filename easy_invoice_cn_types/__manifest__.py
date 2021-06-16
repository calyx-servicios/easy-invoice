# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Easy Invoice CN Types',
    'summary': """
        Creates a configuration menu of 'Types of credit notes' """,
    'author': 'Calyx Servicios S.A., Odoo Community Association (OCA)',
    'maintainers': ['<Github/Gitlab Username/s>'],
    'website': 'http://odoo.calyx-cloud.com.ar/',
    'license': 'AGPL-3',
    'category': 'Technical Settings',
    'version': '11.0.1.0.0',
    'development_status': 'Production/Stable',
    'application': False,
    'installable': True,
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'depends': ['easy_invoice','easy_invoice_employee_cc'],
    'data': [
    #     'security/ir.model.access.csv',
        'views/easy_cn_types_view.xml',
    ],
}
