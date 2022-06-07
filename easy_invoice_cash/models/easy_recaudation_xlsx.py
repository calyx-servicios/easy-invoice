from odoo import models, _
import datetime

DEFAULT_DATE_FROM = datetime.datetime(1900, 1, 1)

class EasyRecaudationXlsx(models.AbstractModel):
    _name = 'report.easy_invoice_cash.report_easy_cashbox_xlsx'
    _description = 'Easy Cashbox Report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        report_name = partners.name
        if partners.partners.report_date_from:
            date_from = partners.report_date_from
        else:
            date_from = DEFAULT_DATE_FROM
        if partners.report_date_to:
            date_to = partners.report_date_to
        else:
            date_to = datetime.datetime.now()
        sheet = workbook.add_worksheet(_("Cashbox Report"))
        bold = workbook.add_format({'bold': True})
        sheet.set_column(0, 0, 11)
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2, 8)
        sheet.set_column(3, 3, 15)
        sheet.set_column(4, 4, 11)
        sheet.set_column(5, 5, 20)
        sheet.set_column(6, 6, 25)
        sheet.set_column(7, 7, 8)
        sheet.set_column(8, 8, 8)

        sheet.write(0, 0, _("Date"), bold)
        sheet.write(0, 1, _("Account Move"), bold)
        sheet.write(0, 2, _("Journal"), bold)
        sheet.write(0, 3, _("Description"), bold)
        sheet.write(0, 4, _("Company"), bold)
        sheet.write(0, 5, _("Account"), bold)
        sheet.write(0, 6, _("Sequence"), bold)
        sheet.write(0, 7, _("State"), bold)
        sheet.write(0, 8, _("Balance"), bold)
        line = 1
        for aml in partners.move_ids:
            if date_from <= aml.date <= date_to:
                sheet.write(line, 0, aml.date)
                sheet.write(line, 1, aml.move_id.name)
                sheet.write(line, 2, aml.journal_id.name)
                sheet.write(line, 3, aml.name)
                sheet.write(line, 4, aml.partner_id.name)
                sheet.write(line, 5, aml.account_id.name)
                sheet.write(line, 6, "-")
                sheet.write(line, 7, "-")
                sheet.write(line, 8, aml.balance)
                line += 1
        for easy_aml in partners.line_recaudation_ids:
            if date_from <= easy_aml.date_pay <= date_to:
                sheet.write(line, 0, easy_aml.date_pay)
                sheet.write(line, 1, easy_aml.invoice_id.name)
                sheet.write(line, 2, "-")
                sheet.write(line, 3, easy_aml.name)
                sheet.write(line, 4, "-")
                sheet.write(line, 5, "-")
                sheet.write(line, 6, easy_aml.sequence_number)
                sheet.write(line, 7, easy_aml.state)
                sheet.write(line, 8, easy_aml.amount_in - easy_aml.amount_out)
                line += 1
        for easy_aml_historic in partners.line_history_ids:
            if date_from <= easy_aml_historic.date_pay <= date_to:
                sheet.write(line, 0, easy_aml_historic.date_pay)
                sheet.write(line, 1, easy_aml_historic.invoice_id.name)
                sheet.write(line, 2, "-")
                sheet.write(line, 3, easy_aml_historic.name)
                sheet.write(line, 4, "-")
                sheet.write(line, 5, "-")
                sheet.write(line, 6, easy_aml_historic.sequence_number)
                sheet.write(line, 7, easy_aml_historic.state)
                sheet.write(line, 8, easy_aml_historic.amount_in - easy_aml_historic.amount_out)
                line += 1