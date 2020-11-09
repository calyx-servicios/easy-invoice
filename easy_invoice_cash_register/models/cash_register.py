from odoo import api, exceptions, fields, models, _
from odoo.tools import float_is_zero, float_compare, pycompat
from odoo.tools.misc import formatLang

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from odoo.addons import decimal_precision as dp
import logging
import pytz

_logger = logging.getLogger(__name__)

class EasyInvoiceCashRegister(models.Model):
    _name = "easy.invoice.cash.register"
    _description = "Easy Invoice Cash Register"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = "name desc"

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id

    @api.multi
    @api.depends('journal_ids')
    def _compute_journals(self):
        total = 0.0
        for journal in self.journal_ids:
            if journal.type == 'cash': 
                currency = self.currency_id
                account_sum = 0
                account_ids = tuple(ac for ac in [journal.default_debit_account_id.id, journal.default_credit_account_id.id] if ac)
                if account_ids:
                    amount_field = 'balance' if (not journal.currency_id or journal.currency_id == self.company_id.currency_id) else 'amount_currency'
                    query = """SELECT sum(%s) FROM account_move_line WHERE account_id in %%s AND date <= %%s;""" % (amount_field,)
                    self.env.cr.execute(query, (account_ids, fields.Date.today(),))
                    query_results = self.env.cr.dictfetchall()
                    if query_results and query_results[0].get('sum') != None:
                        account_sum = query_results[0].get('sum')
                total += account_sum
        self.amount_journal = total


    @api.multi
    @api.depends('easy_recaudation_ids')
    def _compute_easy(self):
        total = 0.0
        for rec in self.easy_recaudation_ids:
            total += rec.amount_box
        self.amount_easy = total


    @api.multi
    @api.depends('amount_journal', 'amount_easy')
    def _compute_total(self):
        self.amount_total = self.amount_easy + self.amount_journal

    @api.multi
    @api.depends('amount_total', 'effective_count')
    def _compute_difference(self):
        self.difference = self.effective_count - self.amount_total

    @api.one
    @api.depends('easy_recaudation_id')
    def _compute_related_amount(self):
        self.recaudation_related_amount = self.easy_recaudation_id.amount_box

    @api.one
    def partial_close(self):
        self.easy_recaudation_id.partial_close(self.difference, self.description)
        self.state = 'arched'

    @api.model
    def _get_default_name(self):
        user = self.env['res.users'].browse(self.env.uid)
        tz = pytz.timezone(user.tz) if user.tz else pytz.utc
        print (tz)
        print (tz)
        print (tz)
        print (tz)
        return fields.datetime.now(tz).strftime("%m/%d/%y %H:%M:%S")

    name = fields.Char(string="Name", default=_get_default_name)
    state = fields.Selection([
            ('draft','Draft'),
            ('arched', 'Arched'),
        ], string='Status', index=True, readonly=True, default='draft',copy=False,)
    journal_ids = fields.Many2many('account.journal', required=True, string='Journals', readonly=True, states={'draft': [('readonly', False)]})
    easy_recaudation_ids = fields.Many2many('easy.recaudation',  string='Easy Recaudations', required=True, readonly=True, states={'draft': [('readonly', False)]})
    amount_journal = fields.Monetary(string='Total Journals', store=True, readonly=True, compute='_compute_journals', )
    amount_easy = fields.Monetary(string='Total Easy', store=True, readonly=True, compute='_compute_easy')
    easy_recaudation_id = fields.Many2one('easy.recaudation',  string='Easy Recaudations to Adjustment', readonly=True, states={'draft': [('readonly', False)]})
    recaudation_related_amount = fields.Float(string='Recaudation Amount', store=True, readonly=True, compute='_compute_related_amount')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_compute_total')
    effective_count = fields.Monetary(string='Effective Cunt', readonly=True, states={'draft': [('readonly', False)]})
    difference = fields.Monetary(string='Difference', store=True, readonly=True, compute='_compute_difference')
    currency_id = fields.Many2one('res.currency', string='Currency',
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        default=_default_currency, track_visibility='always')
    company_id = fields.Many2one('res.company', 'Company', \
        default=lambda self: self.env['res.company']._company_default_get('easy.invoice.cash.register'), readonly=True, states={'draft': [('readonly', False)]})
    description = fields.Char('Description')
    user_id = fields.Many2one('res.users', string='Responsable', index=True, track_visibility='onchange', default=lambda self: self.env.user, readonly=True)