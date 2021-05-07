from odoo import api, fields, models, _, exceptions
from odoo.exceptions import UserError, ValidationError

class CustomerInvoiceReport(models.TransientModel):
    _name = 'invoice.report'
    
    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')

    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        data = self.read()[0]
        report = self.env.ref(
            'easy_invoice_customer_invoice.customer_invoice_report')
        return report.report_action(self, data=data)
