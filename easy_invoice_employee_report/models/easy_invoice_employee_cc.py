# © 2016 Julien Coux (Camptocamp)
# © 2018 Forest and Biomass Romania SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.tools import float_is_zero
from ast import literal_eval
from odoo.exceptions import AccessError, UserError
import logging

_logger = logging.getLogger(__name__)


class EasyEmployeeCCType(models.Model):
    """ 
    WARNING:
    This module was created due to easy employee cc poor design
    I needed to solve 'type hardcoded' with this entity to allow normal type filtering with many2many widgets
    The right way to solve this is to fix the 'type' field in easy_invoice_employee_cc module.
    """

    _name = 'easy.employee.cc.type'
    name = fields.Char()
    type = fields.Selection([('advancement', 'Advancement'),
                             ('bank', 'Bank'),
                             ('basic_salary', 'Basic Salary'),
                             ('liquidation_salary', 'Liquidation Salary'),
                             ], string="Type", default='advancement')
    

    _sql_constraints = [('name_of_field_unique', 'unique(name)', 'Unique')]


class EasyEmployeeCC(models.Model):
    _inherit = "easy.employee.cc"

    settlement_type = fields.Selection(
        [
            ("haberes", "Haberes"),
            ("pagos_compesacion", "Pagos y Compensaciones"),
        ],
        string="Type",
        related="easy_employe_cc_settlement_id.ttype",
        store=True,
    )