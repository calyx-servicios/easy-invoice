# -*- coding: utf-8 -*-
# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, exceptions, fields, models, _
from odoo.tools import float_is_zero, float_compare, pycompat
from odoo.tools.misc import formatLang

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

#### Fields
    invoice_line_id = fields.Many2one('easy.invoice.line', string='Invoice Line',  )
    employee_cc_id = fields.Many2one('easy.employee.cc', string='Employee CC', )
    employee_expense_id = fields.Many2one('easy.employee.expense', string='Employee Expense', )
#### end Fields

