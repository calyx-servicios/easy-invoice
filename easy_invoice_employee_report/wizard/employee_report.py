# Copyright 2016 Camptocamp SA
# Copyright 2017 Akretion - Alexis de Lattre
# Copyright 2018 Eficent Business and IT Consuting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.tools import pycompat
from odoo.exceptions import UserError, ValidationError


class EmployeetReportWizard(models.TransientModel):
    """Employee Report Wizard."""

    _name = "employee.report.wizard"
    _description = "Employee Report Wizard"

    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.user.company_id,
        required=False,
        string='Company'
    )
    company_ids = fields.Many2many(
        comodel_name='res.company',
        string='Filter Companies',
    )
    date_range_id = fields.Many2one(
        comodel_name='date.range',
        string='Date range'
    )
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)

    account_ids = fields.Many2many(
        comodel_name='hr.employee',
        string='Employees',
    )

    settlement_type = fields.Selection(
        [("haberes", "Haberes"), ("pagos_compesacion", "Pagos y Compensaciones")], string="Easy Movement"
    )
    easy_employe_cc_settlement_ids = fields.Many2many(
        comodel_name='easy.employe.cc.settlement', string="Concept"
    )

    description = fields.Char(string='Description')

    detail = fields.Boolean(string='Detail')

    

    

    @api.onchange('date_range_id')
    def onchange_date_range_id(self):
        """Handle date range change."""
        self.date_from = self.date_range_id.date_start
        self.date_to = self.date_range_id.date_end
        

    @api.multi
    def button_export_html(self):

        self.ensure_one()
        action = self.env.ref(
            'easy_invoice_employee_report.action_report_employee_html')
        vals = action.read()[0]
        context1 = vals.get('context', {})
        if isinstance(context1, pycompat.string_types):
            context1 = safe_eval(context1)
        model = self.env['report_employee']
        report = model.create(self._prepare_report())
        report.compute_data_for_report()

        context1['active_id'] = report.id
        context1['active_ids'] = report.ids
        vals['context'] = context1
        return vals

    @api.multi
    def button_export_xlsx(self):

        self.ensure_one()
        action = self.env.ref(
            'easy_invoice_employee_report.action_report_employee_xlsx')
        
        vals = action.read()[0]
        context1 = vals.get('context', {})
        if isinstance(context1, pycompat.string_types):
            context1 = safe_eval(context1)
        model = self.env['report_employee']
        report = model.create(self._prepare_report())
        report.compute_data_for_report()

        context1['active_id'] = report.id
        context1['active_ids'] = report.ids
        vals['context'] = context1
        return vals

    def _prepare_report(self):
        self.ensure_one()
        return {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'filter_company_ids': [(6, 0, self.company_ids.ids)],
            # no lo voy a setear nunca porque esto fue mal especificado aho uso settlement_ids
            #'filter_type_ids': [(6, 0, self.type_ids.ids)],
            'filter_account_ids': [(6, 0, self.account_ids.ids)],
            'description': self.description,
            'detail': self.detail,
            'filter_settlement_ids': [(6, 0, self.easy_employe_cc_settlement_ids.ids)],
            'filter_settlement_type': self.settlement_type,
        }
