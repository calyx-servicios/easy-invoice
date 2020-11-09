# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ProductCategory(models.Model):
    _inherit = "product.category"

    account_analytic = fields.Boolean(
        string="Not account analytic for product"
    )
