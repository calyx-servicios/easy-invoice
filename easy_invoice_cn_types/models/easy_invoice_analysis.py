from odoo import fields, models, tools, api

class AnalysisReportLine(models.Model):
    """ Easy Analysis Report"""

    _inherit = 'easy_invoice_analysis_report'

    @api.model
    def _get_type_refund_picker(self):
        lst = []
        cn_types_ids = self.env['easy.invoice.cn.types'].search([])
        for cn_types in cn_types_ids:
            lst.append((str(cn_types.cn_types_value), str(cn_types.cn_types_name)))
        return lst

    type_refund = fields.Selection('_get_type_refund_picker')