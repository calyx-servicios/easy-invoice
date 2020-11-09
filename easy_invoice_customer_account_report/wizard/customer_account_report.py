# Copyright 2016 Camptocamp SA
# Copyright 2017 Akretion - Alexis de Lattre
# Copyright 2018 Eficent Business and IT Consuting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.tools import pycompat
from odoo.exceptions import UserError, ValidationError


class CustomerAccountReportWizard(models.TransientModel):
    """Customer Account Report Wizard."""

    _name = "customer.account.report.wizard"
    _description = "Customer Account Report Wizard"

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
        comodel_name='res.partner',
        string='Partners',
    )

    non_zero = fields.Boolean('Non Zero', default=True)

    @api.onchange('date_range_id')
    def onchange_date_range_id(self):
        """Handle date range change."""
        self.date_from = self.date_range_id.date_start
        self.date_to = self.date_range_id.date_end

    @api.multi
    def _export(self, report_name):
        self.ensure_one()
        action = self.env.ref(
            report_name)
        vals = action.read()[0]
        context1 = vals.get('context', {})
        if isinstance(context1, pycompat.string_types):
            context1 = safe_eval(context1)
        model = self.env['report_customer_account']
        report = model.create(self._prepare_report())
        report.compute_data_for_report()

        context1['active_id'] = report.id
        context1['active_ids'] = report.ids
        vals['context'] = context1
        return vals

    @api.multi
    def button_export_html(self):
        return self._export(
            'easy_invoice_customer_account_report.action_report_customer_account_html')

    @api.multi
    def button_export_xlsx(self):
        return self._export(
            'easy_invoice_customer_account_report.action_report_customer_account_xlsx')

    def _prepare_report(self):
        self.ensure_one()
        return {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'company_id': self.company_id.id,
            'filter_account_ids': self.account_ids and [(6, 0, self.account_ids.ids)],
            'non_zero': self.non_zero,
        }
