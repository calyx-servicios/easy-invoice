from odoo import api, fields, models, _, exceptions
from odoo.exceptions import UserError, ValidationError

class CreditNoteReport(models.TransientModel):
    _name = 'credit.note.report'
    
    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')

    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        data = self.read()[0]
        report = self.env.ref(
            'easy_invoice_credit_note.customer_credit_note_report')
        return report.report_action(self, data=data)
