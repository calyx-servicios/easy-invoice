from odoo import api, models


class EasyPaymentGroup(models.Model):

    _inherit = "easy.payment.group"

    
    @api.multi
    def print_easypaymentgroup(self):
    
        return self.env.ref(
            "easy_invoice_reports.action_report_easy_paymentgroup"
        ).report_action(self)

    @api.multi
    def print_easypayment(self):
    
        return self.env.ref(
            "easy_invoice_reports.action_report_easy_paymentgroup"
        ).report_action(self)
