from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class EasyInvoice(models.Model):
    _inherit = "easy.invoice"

    @api.model
    def _get_type_refund_picker(self):
        lst = []
        cn_types_ids = self.env['easy.invoice.cn.types'].search([])
        for cn_types in cn_types_ids:
            lst.append((str(cn_types.cn_types_value), str(cn_types.cn_types_name)))
        return lst

    type_refund = fields.Selection('_get_type_refund_picker')
