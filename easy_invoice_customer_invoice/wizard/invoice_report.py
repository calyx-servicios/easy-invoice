from odoo import api, fields, models, _, exceptions
from odoo.exceptions import UserError, ValidationError

class CustomerInvoiceReport(models.TransientModel):
    _name = 'invoice.report'
    
    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')
    draft = fields.Boolean(default=False)
    open = fields.Boolean(default=True)
    paid = fields.Boolean(default=True)
    cancel = fields.Boolean(default=False)
    account_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Partners',
    )

    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        data = self.read()[0]
        report = self.env.ref(
            'easy_invoice_customer_invoice.customer_invoice_report')
        return report.report_action(self, data=data)
