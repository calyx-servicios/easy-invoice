# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = "hr.employee"

# Fields
    cc_line_ids = fields.One2many('easy.employee.cc', 'employee_id', string='Salary/Advancement')
    amount_residual = fields.Float(string='Residual', readonly=True, compute='_control_aa_amount')  
# end Fields

    @api.multi
    def hook_profiles(self):
        obj_ids = self.env['easy.employee.cc'].search([])
        for o in obj_ids:
            tag_name = []
            if o.type:
                if o.type == 'advancement':
                    tag_name = self.env.ref('easy_invoice_employee_cc.settlement_advancement')
                if o.type == 'bank':
                    tag_name = self.env.ref('easy_invoice_employee_cc.settlement_bank')
                if o.type == 'basic_salary':
                    tag_name = self.env.ref('easy_invoice_employee_cc.settlement_basic_salary')
                if o.type == 'liquidation_salary':
                    tag_name = self.env.ref('easy_invoice_employee_cc.settlement_liquidation_salary')
                # _logger.info('Entro ==> %s ' %(tag_name))
                if not o.easy_employe_cc_settlement_id:
                    if tag_name:
                        o.easy_employe_cc_settlement_id = tag_name.id
            if not o.type:
                o.easy_employe_cc_settlement_id = False

    @api.multi
    @api.depends('cc_line_ids.amount_salary', 'cc_line_ids.amount_advancement')
    def _control_aa_amount(self):
        for rec in self:
            amount_residual = 0.0
            for line_obj in rec.cc_line_ids:
                amount_residual -= line_obj.amount_advancement  # *(-1.0)
                amount_residual += line_obj.amount_salary  # *(-1.0)
            rec.amount_residual = amount_residual

    @api.constrains('identification_id')
    def _check_id_duplicates(self):
        employees = self.env['hr.employee'].search([('identification_id', '=', self.identification_id)])

        for employee in employees:
            if employee.name != self.name:
                raise ValidationError(_('The Employee %s already has the Identification Number %s') % (employee.name, self.identification_id))
