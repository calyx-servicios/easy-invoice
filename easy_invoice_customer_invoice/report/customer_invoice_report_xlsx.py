# coding: utf-8
from datetime import datetime
import base64
import io

from odoo import models, _


class CustomerInvoiceReportXLSX(models.AbstractModel):
    _name = "report.easy_invoice_customer_invoice.invoice_report"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, objs):

        #
        # Helper Method
        #
        def _format_date(date_utc_format):
            """Change the UTC format used by Odoo for dd-mm-yyyy

            Arguments:
                date_utc_format {str} -- Date UTC format yyyy-mm-dd

            Returns:
                str -- Date in dd-mm-yyyy format.
            """
            date_d_m_y_format = datetime.strptime(
                date_utc_format, "%Y-%m-%d"
            ).strftime("%d-%m-%Y")
            return date_d_m_y_format

        #
        # Formatting
        #
        heading_format = workbook.add_format(
            {
                "align": "center",
                "valign": "vcenter",
                "bold": True,
                "size": 10,
                "top": 1,
                "bottom": 1,
                "font": "arial",
            }
        )

        heading_format_no_borders = workbook.add_format(
            {"align": "center", "valign": "vcenter", "bold": True, "size": 12}
        )

        sub_heading_format = workbook.add_format(
            {"align": "center", "valign": "vcenter", "bold": True, "size": 11,}
        )

        sub_heading_acc_format = workbook.add_format(
            {"align": "center", "valign": "vcenter", "bold": True, "size": 11,}
        )

        center_format = workbook.add_format(
            {"align": "center", "valign": "vcenter","font": "arial", "size": 10,}
        )
        
        right_format = workbook.add_format(
            {"align": "right", "valign": "vcenter","font": "arial", "size": 10,}
        )
        
        left_format = workbook.add_format(
            {"align": "left", "valign": "vcenter","font": "arial", "size": 10,}
        )

        monetary_format = workbook.add_format(
            {"num_format": "#,##0.00", "align": "center", "valign": "vcenter",}
        )

        date_range_format = workbook.add_format(
            {"align": "center", "valign": "vcenter", "bold": True, "size": 12,}
        )

        #
        # Adding Sheet
        #
        column = 0
        row = 0
        worksheet = workbook.add_worksheet(_("Reporte de Facturacion"))

        #
        # Width of the Columns
        #
        worksheet.set_column(row, column, 30)
        worksheet.set_column(row + 1, column + 1, 28)
        worksheet.set_column(row + 2, column + 2, 21)
        worksheet.set_column(row + 3, column + 3, 6)
        worksheet.set_column(row + 4, column + 4, 8)
        worksheet.set_column(row + 5, column + 5, 12)
        worksheet.set_column(row + 6, column + 6, 8)
        worksheet.set_column(row + 7, column + 7, 8)
        worksheet.set_column(row + 8, column + 8, 13)

        #
        # Reporte de Facturacion Query and Titles
        #
        states = []
        if objs.draft:
            states.append("draft")
        if objs.open:
            states.append("open")
        if objs.paid:
            states.append("paid")
        if objs.cancel:
            states.append("cancel")
        
        partner_ids = []
        for partner in objs.account_ids:
            partner_ids.append(partner.id)
        if partner_ids:
            account_move_objs = self.env["easy.invoice.line"].search(
                [
                    ("date_invoice", ">=", objs.date_from),
                    ("date_invoice", "<=", objs.date_to),
                    ("invoice_state", "in", states),
                    ("invoice_type", "=", "out_invoice"),
                    ("company_id", "=", self.env.user.company_id.id),
                    ("partner_id.id", "in", partner_ids)
                ],
                order="date_invoice asc",
            )
        else:
            account_move_objs = self.env["easy.invoice.line"].search(
                [
                    ("date_invoice", ">=", objs.date_from),
                    ("date_invoice", "<=", objs.date_to),
                    ("invoice_state", "in", states),
                    ("invoice_type", "=", "out_invoice"),
                    ("company_id", "=", self.env.user.company_id.id),
                ],
                order="date_invoice asc",
            )

        #
        # Reporte de Facturacion Manipulation
        #
        worksheet.write(row, column, "CLIENTES", heading_format)
        worksheet.write(row, column + 1 , "PRODUCTOS", heading_format)
        worksheet.write(row, column + 2, "RUBRO", heading_format)
        worksheet.write(row, column + 3, "UDM", heading_format)
        worksheet.write(row, column + 4, "CANTIDAD", heading_format)
        worksheet.write(row, column + 5, "PRECIO UNIT", heading_format)
        worksheet.write(row, column + 6, "TOTAL", heading_format)
        worksheet.write(row, column + 7, "FECHA", heading_format)
        worksheet.write(row, column + 8, "NRO DOCUMENTO", heading_format)
        row += 1
        for move in account_move_objs:

            worksheet.write(row, column, move.partner_id.name, left_format)
            worksheet.write(row, column + 1, move.product_id.name, left_format)
            worksheet.write(row, column + 2, move.product_id.categ_id.name, left_format)
            worksheet.write(row, column + 3, move.product_id.uom_id.name, left_format)            
            worksheet.write(row, column + 4, move.quantity, center_format)
            worksheet.write(row, column + 5, move.price_unit, center_format)
            worksheet.write(row, column + 6, move.price_subtotal, center_format)
            worksheet.write(row, column + 7, _format_date(move.date_invoice), center_format)
            worksheet.write(row, column + 8, move.invoice_id.name, right_format)
            
            row += 1
