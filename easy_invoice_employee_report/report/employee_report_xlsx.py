# Author: Julien Coux
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, models
import logging

_logger = logging.getLogger(__name__)


class EmployeeXlsx(models.AbstractModel):
    _name = 'report.report_employee_xlsx'
    _inherit = 'report.account_financial_report.abstract_report_xlsx'

    def _get_report_name(self, report):
        report_name = _('Employees Report')
        return self._get_report_complete_name(report, report_name)

    def _get_report_columns(self, report):


        res = {
            0: {'header': _('Employee'),
                'field': 'employee_id',
                'type': 'many2one',
                'width': 30},
            1: {'header': _('Type'),
                'field': 'type_id',
                'type': 'many2one',
                'width': 30},
            2: {'header': _('Settlement Type'),
                'field': 'settlement_type',
                'width': 20},
            3: {'header': _('Date'),
                'field': 'date',
                'width': 20},
            4: {'header': _('Description'),
                'field': 'description',
                'width': 20},
            5: {'header': _('Amount'),
                'field': 'total',
                'type': 'amount',
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

        for _type in report.type_ids:
            self.write_type_line(_type)
            if report.detail:
                for employee in _type.employee_ids:
                    self.write_employee_line(employee)
                    for account in employee.move_ids:
                        self.write_move_line(account)

    def write_employee_line(self, line_object):
        """Write a line on current line using all defined columns field name.
        Columns are defined with `_get_report_columns` method.
        """

        cell_format = self.format_amount
        for col_pos, column in self.columns.items():

            if column.get('field', False) in ('employee_id'):
                self.sheet.write_string(
                    self.row_pos, col_pos, line_object.employee_id.name, self.format_bold)
            
            if column.get('field', False) in ('total'):
                value = line_object.total or 0.0
                self.sheet.write_number(
                    self.row_pos, col_pos, float(value), self.format_bold
                )

        self.row_pos += 1

    def write_type_line(self, line_object):
        """Write a line on current line using all defined columns field name.
        Columns are defined with `_get_report_columns` method.
        """

        cell_format = self.format_amount
        for col_pos, column in self.columns.items():

            if column.get('field', False) in ('type_id'):
                self.sheet.write_string(
                    self.row_pos, col_pos, line_object.type_id.name or _('Concept Type not assigned'), self.format_bold)
            
            if column.get('field', False) in ('total'):
                value = line_object.total or 0.0
                self.sheet.write_number(
                    self.row_pos, col_pos, float(value), self.format_bold
                )

        self.row_pos += 1

    def write_move_line(self, line_object):
        """Write a line on current line using all defined columns field name.
        Columns are defined with `_get_report_columns` method.
        """

        cell_format = self.format_amount
        for col_pos, column in self.columns.items():

            if column.get('field', False) in ('employee_id'):
                self.sheet.write_string(
                    self.row_pos, col_pos, line_object.employee_id.employee_id.name)
            if column.get('field', False) in ('type_id'):
                self.sheet.write_string(
                    self.row_pos, col_pos, line_object.employee_id.type_id.type_id.name)
            if column.get('field', False) in ('settlement_type'):
                settlement_type = line_object.settlement_type or ''
                self.sheet.write_string(
                    self.row_pos, col_pos, settlement_type)
            if column.get('field', False) in ('description'):
                self.sheet.write_string(
                    self.row_pos, col_pos, line_object.description)
            if column.get('field', False) in ('date'):
                self.sheet.write_string(
                    self.row_pos, col_pos, line_object.date)
            if column.get('field', False) in ('total'):
                value = line_object.total or 0.0
                self.sheet.write_number(
                    self.row_pos, col_pos, float(value)
                )

        self.row_pos += 1
