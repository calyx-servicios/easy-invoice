# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import itertools
import psycopg2

from odoo.addons import decimal_precision as dp

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, RedirectWarning, except_orm
from odoo.tools import pycompat
import logging

_logger = logging.getLogger(__name__)

class ProductCategory(models.Model):
    _inherit = "product.category"
    _order='level,sequence'

    analytic = fields.Boolean(string='Calculation Category',default=False,
        help="Specify if the category can be selected for Analytic Accounting Calculation Dashboard.")

    level = fields.Integer(string='Level',compute='_set_level', readonly=True, store=True)
    sequence = fields.Integer(string='Sequence',default=0)

    #very stupid field
    category_name = fields.Char(
        'Category', compute='_compute_category_name',
        store=True)
    #another very stupid field
    sub_category_name = fields.Char(
        'SubCategory', compute='_compute_category_name',
        store=True)

    @api.depends('name', 'parent_id.complete_name')
    def _compute_category_name(self):
        for category in self:
            _logger.debug('category to recompute :%s', category.name)
            if category.parent_id:
                sub_name= '/ %s ' % category.name
                trim = len(sub_name)
                index=len(category.complete_name)-trim
                category.category_name = category.complete_name[:index]
                category.sub_category_name= category.name
            else:
                category.category_name = category.name
                category.sub_category_name= ''

    @api.multi
    @api.depends('sequence','parent_id','parent_id.sequence','child_id','child_id.sequence')
    def _set_level(self, level=1):

        for category in self:
            _logger.debug('geting level for %s' % category.display_name)
            category.level=level
            for child in category.child_id:
                child._set_level(level+1)
