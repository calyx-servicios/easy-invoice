# Author: Julien Coux
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, models
import logging

_logger = logging.getLogger(__name__)


class CustomerAccountXlsx(models.AbstractModel):
    _name = 'report.report_customer_account_xlsx'
    _inherit = 'report.account_financial_report.abstract_report_xlsx'

    def __init__(self, pool, cr):
        # main sheet which will contains report
        # Formats
        self.format_bold_right = None

    def _define_formats(self, workbook):
        super(CustomerAccountXlsx, self)._define_formats(workbook)
        self.format_bold_right = workbook.add_format({'bold': True,
                                                      'align': 'right'})

    def _get_report_name(self, report):
        report_name = _('Customer Account Report')
        return self._get_report_complete_name(report, report_name)

    def _get_report_columns(self, report):

        res = {
            0: {'header': _('Date'),
                'field': 'move_date',
                'width': 30},
            1: {'header': _('Description'),
                'field': 'description',
                'width': 30},
            2: {'header': _('Type Refund'),
                'field': 'type_refund',
                'width': 30},
            3: {'header': _('Debit'),
                'field': 'debit',
                'type': 'amount',
                'width': 20},
            4: {'header': _('Credit'),
                'field': 'credit',
                'type': 'amount',
                'width': 20},
            5: {'header': _('Accumulate'),
                'field': 'computed',
                'type': 'amount',
                'width': 20},
            6: {'header': _('Expiry'),
                'field': 'expiry_date',
                'width': 20},
        }

        return res

    def _get_col_count_filter_name(self):
        return 2

    def _get_col_count_filter_value(self):
        return 2

    def _get_report_filters(self, report):
        accounts = []
        companies = []
        for account in report.filter_account_ids:
            accounts.append([_('Account'),
                             _('%s') % (account.name)])
        for company in report.filter_company_ids:
            companies.append([_('Company'),
                              _('%s') % (company.name)])
        filters = []
        filters.append([_('Date range filter'),
                        _('From: %s To: %s') % (report.date_from, report.date_to)])
        if len(companies) > 0:
            for company in companies:
                filters.append(company)
        if len(accounts) > 0:
            for account in accounts:
                filters.append(account)
        return filters

    def _generate_report_content(self, workbook, report):
        # Display array header for account lines
        self.write_array_header()

        for partner in report.partner_ids:
            if partner.visible:
                self.write_partner_line(partner, report)
                for account in partner.move_ids:
                    self.write_line(account)
                    self.write_move_line(account)
                self.write_partner_line_end(partner, report)

    def write_move_line(self, line_object):
        """Write a line on current line using all defined columns field name.
        Columns are defined with `_get_report_columns` method.
        """
        #esto es malisimo, hay que cambiarlo, pero tengo problemas con la traduccion de esto
        labels={'returns': 'Devoluciones',
                'withdrawal': 'Retiro',
                'corrections': 'Correciones',
                'combo': 'Combo (Marketing)',
                'various': 'Varios'}
        cell_format = self.format_amount
        row_pos = self.row_pos-1
        for col_pos, column in self.columns.items():

            if column.get('field', False) in ('type_refund'):
                detail = ''

                if line_object.easy_invoice_id and line_object.easy_invoice_id.type == 'out_refund':
                    datail=''
                    try:
                        detail = labels[line_object.type_refund]
                    except:
                        pass
                self.sheet.write_string(
                    row_pos, col_pos, detail, self.format_bold)

    def write_partner_line(self, line_object, report):
        """Write a line on current line using all defined columns field name.
        Columns are defined with `_get_report_columns` method.
        """

        cell_format = self.format_amount
        for col_pos, column in self.columns.items():

            if column.get('field', False) in ('move_date'):
                self.sheet.write_string(
                    self.row_pos, col_pos, line_object.partner_id.name, self.format_bold)
            if column.get('field', False) in ('credit'):
                self.sheet.write_string(
                    self.row_pos, col_pos, 'Inicial:', self.format_bold_right)
            if column.get('field', False) in ('computed'):
                value = line_object.initial or 0.0
                self.sheet.write_number(
                    self.row_pos, col_pos, float(value), self.format_bold
                )

        self.row_pos += 1

    def write_partner_line_end(self, line_object, report):
        """Write a line on current line using all defined columns field name.
        Columns are defined with `_get_report_columns` method.
        """

        cell_format = self.format_amount
        for col_pos, column in self.columns.items():

            if column.get('field', False) in ('move_date'):
                self.sheet.write_string(
                    self.row_pos, col_pos, line_object.partner_id.name, self.format_bold)
            if column.get('field', False) in ('credit'):
                self.sheet.write_string(
                    self.row_pos, col_pos, 'Final:', self.format_bold)
            if column.get('field', False) in ('computed'):
                value = line_object.final or 0.0
                self.sheet.write_number(
                    self.row_pos, col_pos, float(value), self.format_bold_right
                )

        self.row_pos += 1
