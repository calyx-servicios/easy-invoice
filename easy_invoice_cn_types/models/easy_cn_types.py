from odoo import fields, models, _, api
from odoo.exceptions import Warning, ValidationError


class EasyCNTypes(models.Model):
    _name = "easy.invoice.cn.types"
    _rec_name = "cn_types_name"
    _order = "sequence"

    cn_types_name = fields.Char("Name")
    cn_types_value = fields.Char("Value")
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)

    _sql_constraints = [('unique_cn_types_value', 'unique (cn_types_value)', 'value must be unique')]

    def unlink(self):
        sale_obj = self.env["easy.invoice"]
        rule_ranges = sale_obj.search([("type_refund", "=", self.cn_types_value)])
        if rule_ranges:
            raise Warning(
                _(
                    "You are trying to delete a record "
                    "that is still referenced in one o more invoice, "
                    "try to archive it."
                )
            )
        return super(EasyCNTypes, self).unlink()

    @api.multi
    def write(self, vals):
        sale_obj = self.env["easy.invoice"]
        rule_ranges = sale_obj.search([("type_refund", "=", self.cn_types_value)])
        if self.cn_types_value != vals.get("cn_types_value") and rule_ranges:
            raise Warning(
                _(
                    "You are trying to edit a record "
                    "that is still referenced in one o more invoice, "
                    "try to archive it."
                )
            )
        return super(EasyCNTypes, self).write(vals)
