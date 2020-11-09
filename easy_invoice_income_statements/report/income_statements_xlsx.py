# Author: Julien Coux
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from datetime import date, datetime
from odoo import _,api, fields, models
import logging
_logger = logging.getLogger(__name__)

class IncomeStatementsXslx(models.AbstractModel):
    _name = 'report.report_income_statements_xlsx'
    _inherit = 'report.account_financial_report.abstract_report_xlsx'

    def _get_report_name(self, report):
        report_name = _('Income Statements')
        return self._get_report_complete_name(report, report_name)

    def _get_report_columns(self, report):
        if report.show_lines:
            res = {
            0: {'header': _('Code'), 'field': 'code', 'width': 30},
            1: {'header': _('Account'),
                'field': 'account_id',
                'type': 'many2one',
                'width': 30},
            2: {'header': _('Category'),
                'field': 'category_id',
                'type': 'many2one',
                'width': 20},
            3: {'header': _('SubCategory'),
                'field': 'category_id',
                'type': 'many2one',
                'width': 20},
            4: {'header': _('Product'),
                'field': 'product_id',
                'type': 'many2one',
                'width': 20},}
            count = len(res.keys())
            for child in report.child_ids:
                total = 0
                month=datetime.strptime(child.date_from,"%Y-%m-%d")
                month=month.strftime("%b-%Y")
                column = {count: {'header': _(month),
                    'field': _('balance'),
                    'type': 'amount',
                    'report_id': child.id,
                    'width': 14},}
                res = {**res, **column}
                count+=1
            
            column = {count: {'header': _('Balance'),
                'field': 'balance',
                'type': 'amount',
                'width': 14},
                }
            res = {**res, **column}
            count+=1 
        else:
            res = {
                0: {'header': _('Category'), 'field': 'name', 'width': 30},}
            count = len(res.keys())
            for child in report.child_ids:
                total = 0
                month=datetime.strptime(child.date_from,"%Y-%m-%d")
                month=month.strftime("%b-%Y")
                column = {count: {'header': _(month),
                    'field': _('balance'),
                    'type': 'amount',
                    'report_id': child.id,
                    'width': 14},}
                res = {**res, **column}
                count+=1
            
            column = {count: {'header': _('Balance'),
                'field': 'balance',
                'type': 'amount',
                'width': 14},
                }
            res = {**res, **column}
            count+=1
            
        return res
    def _get_col_count_filter_name(self):
        return 2

    def _get_col_count_filter_value(self):
        return 2

    def _get_report_filters(self, report):
        categories=[]
        accounts=[]
        products=[]
        for category in report.filter_category_ids:
            categories.append([_('Category'),
             _('%s') % (category.complete_name)])
        for account in report.filter_account_ids:
            accounts.append([_('Account'),
             _('%s %s') % (account.code,account.name)])
        for product in report.filter_product_ids:
            products.append([_('Product'),
             _('%s') % (product.name)])
        filters=[]
        filters.append([_('Date range filter'),
         _('From: %s To: %s') % (report.date_from, report.date_to)])
        if len(categories)>0:
            for category in categories:
                filters.append(category)
        if len(accounts)>0:
            for account in accounts:
                filters.append(account)
        if len(products)>0:
            for product in products:
                filters.append(product)
        return filters

    def _generate_report_content(self, workbook, report):

        # Display array header for account lines
        self.write_array_header()

        # For each account
        for category in report.category_ids:

            if not category.hide_category:
                if report.show_lines:
                    self.write_category_line(category, report)
                    for account in category.account_ids:
                        
                        self.write_line(account)
                        self.write_line_custom(account, category, report)

                else:
                    self.write_category_line(category, report)


    def write_line_custom(self, line_object, category, report):
        """Write a line on current line using all defined columns field name.
        Columns are defined with `_get_report_columns` method.
        """

        row_pos=self.row_pos-1
        cell_format = self.format_amount
        for col_pos, column in self.columns.items():
            if column.get('header',False) in _('Category'):
                value = line_object.category_id.category_name or ''
                self.sheet.write_string(
                    row_pos, col_pos, value, self.format_bold)
                value = line_object.category_id.sub_category_name or ''
                self.sheet.write_string(
                    row_pos, col_pos+1, value, self.format_bold)
            ##split by month
            for month in report.child_ids:
                if column.get('report_id',False) and column['report_id'] == month.id:
                    value=0.0
                    month_account=self.env['report_income_statements_account'].search([
                        ('report_id','=',month.id),
                        ('category_id','=',category.category_id.id),
                        ('product_id','=',line_object.product_id.id),
                        ('account_id','=',line_object.account_id.id)])
                    for account in month_account:
                        value+=account.balance
                    

                    self.sheet.write_number(
                        row_pos, col_pos, float(value), cell_format
                    )
            ########

    def write_line_category_custom(self, line_object):
        """Write a line on current line using all defined columns field name.
        Columns are defined with `_get_report_columns` method.
        """
        row_pos=self.row_pos-1
        cell_format = self.format_amount
        for col_pos, column in self.columns.items():
            if column.get('header',False) in _('Category'):
                value = line_object.category_name or ''
                self.sheet.write_string(
                    row_pos, col_pos, value, self.format_bold)
                value = line_object.sub_category_name or ''
                self.sheet.write_string(
                    row_pos, col_pos+1, value, self.format_bold)




    def write_category_line(self, line_object, report):
        """Write a line on current line using all defined columns field name.
        Columns are defined with `_get_report_columns` method.
        """

        cell_format = self.format_amount
        for col_pos, column in self.columns.items():
            if column.get('header',False) in _('Category'):
                value = line_object.category_id.category_name or ''
                self.sheet.write_string(
                    self.row_pos, col_pos, value, self.format_bold)
                value = line_object.category_id.sub_category_name or ''
                self.sheet.write_string(
                    self.row_pos, col_pos+1, value, self.format_bold)
            if column.get('field',False) in ('balance'):
                value = getattr(line_object, column['field'])
                if line_object.percentage:
                    value=value/100.0
                self.sheet.write_number(
                    self.row_pos, col_pos, float(value), cell_format
                )
            #split by month
            for month in report.child_ids:
                if column.get('report_id',False) and column['report_id'] == month.id:
                    month_account=self.env['report_income_statements_category'].search([
                        ('report_id','=',month.id),
                        ('category_id','=',line_object.category_id.id)])
                    value = 0.0
                    for month_category in month_account:
                        value += month_category.balance
                    self.sheet.write_number(
                        self.row_pos, col_pos, float(value), cell_format
                    )
            #########
            if column.get('field',False) in ('code'):
                self.sheet.write_string(
                    self.row_pos, col_pos, line_object.name, self.format_bold)


        self.row_pos += 1

