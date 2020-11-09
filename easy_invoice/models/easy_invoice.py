from odoo import api, exceptions, fields, models, _
from odoo.tools import float_is_zero, float_compare, pycompat
from odoo.tools.misc import formatLang

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from odoo.addons import decimal_precision as dp
import logging
import pytz

_logger = logging.getLogger(__name__)


class EasyInvoice(models.Model):
    _name = "easy.invoice"
    _description = "Easy Invoice"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = "date_invoice desc"

    @api.multi
    @api.depends("name")
    def name_get(self):
        res = []
        for invoice in self:
            name = invoice.name
            if invoice.type in ('in_invoice', 'in_refund'):
                name = invoice.number
            res.append((invoice.id, name))
        return res

    @api.onchange('amount_total')
    def _onchange_amount_total(self):
        for inv in self:
            if float_compare(inv.amount_total, 0.0, precision_rounding=inv.currency_id.rounding) == -1:
                raise ValidationError(
                    _('You cannot validate an invoice with a negative total amount. You should create a credit note instead.'))

    @api.depends('invoice_line_ids.price_subtotal', 'currency_id', 'company_id', 'date_invoice', 'type')
    def _compute_amount(self):
        round_curr = self.currency_id.round
        self.amount_total = sum(
            line.price_subtotal for line in self.invoice_line_ids)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_signed = self.amount_total * sign

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id

    @api.model
    def _default_sequence(self):
        self_ids = self.env['easy.sequence'].search([])
        if self_ids:
            return self_ids[0]
        return None

    @api.model
    def _default_date_invoice(self):
        user = self.env['res.users'].browse(self.env.uid)
        tz = pytz.timezone(user.tz) if user.tz else pytz.utc
        d = fields.datetime.now(tz)
        return d

    @api.constrains('number')
    def _check_number_invoice_duplicates(self):
        """
        We check that there are no duplicate numbers for documents from the same partner, type of document and company.
        """
        invoices= self.env['easy.invoice']
        numbers_duplicates= invoices.search([('number', '=', self.number),
                            ('partner_id', '=', self.partner_id.id),
                            ('subtype_invoice', '=', self.subtype_invoice),
                            ('company_id', '=', self.company_id.id)])
        if len(numbers_duplicates)>1:
            raise ValidationError(_('El número de comprobante (%s) debe ser único por tipo de documento y proveedor') % (self.number))

    name = fields.Char(string='Reference/Description', index=True, readonly=True,
                       states={'draft': [('readonly', False)]}, copy=False, default='')
    type = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('in_invoice', 'Supplier Bill'),
        ('out_refund', 'Customer Credit Note'),
        ('in_refund', 'Supplier Credit Note'),
    ], readonly=True, index=True, change_default=True,
        default=lambda self: self._context.get('type', 'out_invoice'),
        track_visibility='always')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
    ], string='Status', index=True, readonly=True, default='draft', copy=False,
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
             " * The 'Open' status is used when user creates invoice, an invoice number is generated. It stays in the open status till the user pays the invoice.\n"
             " * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
             " * The 'Cancelled' status is used when user cancel invoice.")
    sent = fields.Boolean(readonly=True, default=False, copy=False,
                          help="It indicates that the invoice has been sent.")
    partner_id = fields.Many2one('res.partner', string='Partner', change_default=True,
                                 required=True, readonly=True, states={'draft': [('readonly', False)]},
                                 track_visibility='always')
    number = fields.Char(string="Document number")
    note = fields.Text(string="Note")

    date_invoice = fields.Date(string='Invoice Date',
                               readonly=True, states={'draft': [('readonly', False)]}, index=True,
                               help="Keep empty to use the current date", copy=False, default=_default_date_invoice)

    date_expiration = fields.Date(string='Invoice Expiration',
                                  readonly=True, states={'draft': [('readonly', False)]}, index=True,
                                  help="Keep empty to use the current date", copy=False, default=_default_date_invoice)

    date_contable = fields.Date(string='Contable Date',
                                readonly=True, states={'draft': [('readonly', False)]}, index=True,
                                help="Keep empty to use the current date", copy=False, default=_default_date_invoice)

    company_id = fields.Many2one('res.company', string='Company', change_default=True,
                                 required=True, readonly=True, states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env['res.company']._company_default_get('easy.invoice'))
    user_id = fields.Many2one('res.users', string='Salesperson', track_visibility='onchange',
                              readonly=True, states={'draft': [('readonly', False)]},
                              default=lambda self: self.env.user, copy=False)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  required=True, readonly=True, states={'draft': [('readonly', False)]},
                                  default=_default_currency, track_visibility='always')
    amount_total = fields.Monetary(string='Total',
                                   store=True, readonly=True, compute='_compute_amount')
    amount_total_signed = fields.Monetary(string='Total in Invoice Currency', currency_field='currency_id',
                                          store=True, readonly=True, compute='_compute_amount',
                                          help="Total amount in the currency of the invoice, negative for credit notes.")
    invoice_line_ids = fields.One2many('easy.invoice.line', 'invoice_id', string='Invoice Lines', oldname='invoice_line',
                                       readonly=True, states={'draft': [('readonly', False)]},)

    description_refund = fields.Char(string="Description Refund")
    type_refund = fields.Selection([('returns', 'Returns'),              # Devoluciones / Retiro / Correcciones / Combo (marketing) / Varios
                                    # Returns / Withdrawal / Corrections / Combo (marketing) / Various
                                    ('withdrawal', 'Withdrawal'),
                                    ('corrections', 'Corrections'),
                                    ('combo', 'Combo (Marketing)'),
                                    ('various', 'Various'),
                                    ], string="Type Refund", default='various')

    subtype_invoice = fields.Selection([('invoice', 'Invoice'),
                                        ('debit_note', 'Debit Note'),
                                        ], string="SubType Invoice", default='invoice')

    description_debit_note = fields.Char(string="Description Debit Note")
    type_debit_note = fields.Selection([('returns', 'Returns'),              # Devoluciones / Retiro / Correcciones / Combo (marketing) / Varios
                                        # Returns / Withdrawal / Corrections / Combo (marketing) / Various
                                        ('withdrawal', 'Withdrawal'),
                                        ('corrections', 'Corrections'),
                                        ('combo', 'Combo (Marketing)'),
                                        ('various', 'Various'),
                                        ], string="Type Debit Note", default='various')
# para unir con los pagos
    boolean_permit_cancel = fields.Boolean(
        string="Permit Cancel", default=True)
    rectificative_invoice_id = fields.Many2one(
        'easy.invoice', string='Rectificative Invoice Related',)
    invoice_residual_amount_id = fields.Many2one(
        'easy.payment', string='Line Residual',)

    payment_line_ids = fields.One2many(
        'easy.payment', 'invoice_id', string='Payments Lines',)
    # compute='_control_residual_amount'
    residual_amount = fields.Monetary(
        string='Residual Amount', compute='_control_residual_amount')

    configuration_sequence_id = fields.Many2one(
        'easy.sequence',  string="Configuration Sequence", default=_default_sequence)

# ends Field

    @api.multi
    @api.depends('payment_line_ids.amount_in', 'payment_line_ids.amount_out', 'state')
    def _control_residual_amount(self):
        for rec in self:
            residual_amount = 0.0
            for line_obj in rec.payment_line_ids:
                if line_obj.state not in ('cancel'):
                    if rec.type in ('in_refund', 'out_invoice'):
                        residual_amount += line_obj.amount_in - line_obj.amount_out
                    if rec.type in ('out_refund', 'in_invoice'):
                        residual_amount += line_obj.amount_out - line_obj.amount_in
            rec.residual_amount = residual_amount

    @api.multi
    def create_line_residual(self):
        for rec in self:
            amount_total = sum(
                line.price_subtotal for line in self.invoice_line_ids)
            if self.type in ('in_refund', 'out_invoice'):
                vals = {
                    'name': 'Residual',
                    'state': 'open',
                    'type': 'pay_out',
                    'invoice_id': self.id,
                    'amount_total': float(amount_total),
                    'amount_in': float(amount_total),
                    'amount_out': 0.0,
                    'date_pay': self.date_invoice,
                    #'invoice_refund_id': rectificative_obj.invoice_id.id   ,
                    #'payment_group_id': self.id   ,
                }
                line_created = self.env['easy.payment'].create(vals)
                self.invoice_residual_amount_id = line_created.id
            if self.type in ('out_refund', 'in_invoice'):
                vals = {
                    'name': 'Residual',
                    'state': 'open',
                    'type': 'pay_in',
                    'invoice_id': self.id,
                    'amount_total': float(amount_total),
                    'amount_out': float(amount_total),
                    'amount_in': 0.0,
                    'date_pay': self.date_invoice,
                    #'invoice_refund_id': rectificative_obj.invoice_id.id   ,
                    #'payment_group_id': self.id   ,
                }
                line_created = self.env['easy.payment'].create(vals)
                self.invoice_residual_amount_id = line_created.id

    @api.one
    def confirm(self):
        for line_obj in self.invoice_line_ids:
            if line_obj.price_subtotal <= 0.0:
                raise ValidationError(
                    _('You cant not Confirm a Invoice with one line in 0 or Negative.-'))
        if self.amount_total <= 0.0:
            raise ValidationError(
                _('You cant not Confirm a Invoice with Amount Total in 0 or Negative.-'))
        # Facturas
        if self.type == 'out_invoice':
            if self.subtype_invoice == 'invoice':
                if not self.configuration_sequence_id.invoice_out_confirm_sequence_id:
                    raise ValidationError(
                        _('You cant not Confirm a Invoice without Out Confirm Sequence.'))
                if not self.name:
                    self.name = self.configuration_sequence_id.invoice_out_confirm_sequence_id.next_by_id()
            if self.subtype_invoice == 'debit_note':
                if not self.configuration_sequence_id.debit_invoice_out_confirm_sequence_id:
                    raise ValidationError(
                        _('You cant not Confirm a Debit Note without Out Confirm Sequence.'))
                if not self.name:
                    self.name = self.configuration_sequence_id.debit_invoice_out_confirm_sequence_id.next_by_id()
        elif self.type == 'in_invoice':
            if self.subtype_invoice == 'invoice':
                if not self.configuration_sequence_id.invoice_out_confirm_sequence_id:
                    raise ValidationError(
                        _('You cant not Confirm a Invoice without In Confirm Sequence.'))
                if not self.name:
                    self.name = self.configuration_sequence_id.invoice_in_confirm_sequence_id.next_by_id()
            if self.subtype_invoice == 'debit_note':
                if not self.configuration_sequence_id.debit_invoice_out_confirm_sequence_id:
                    raise ValidationError(
                        _('You cant not Confirm a Debit Note without In Confirm Sequence.'))
                if not self.name:
                    self.name = self.configuration_sequence_id.debit_invoice_in_confirm_sequence_id.next_by_id()
        # Rectificativas
        elif self.type == 'in_refund':
            if not self.configuration_sequence_id.refund_invoice_in_confirm_sequence_id:
                raise ValidationError(
                    _('You cant not Confirm a Invoice without Refund In Confirm Sequence.'))
            if not self.name:
                self.name = self.configuration_sequence_id.refund_invoice_in_confirm_sequence_id.next_by_id()
        elif self.type == 'out_refund':
            if not self.configuration_sequence_id.refund_invoice_out_confirm_sequence_id:
                raise ValidationError(
                    _('You cant not Confirm a Invoice without Refund Out Confirm Sequence.'))
            if not self.name:
                self.name = self.configuration_sequence_id.refund_invoice_out_confirm_sequence_id.next_by_id()
        self.create_line_residual()
        self.state = 'open'

    @api.multi
    def back2draft(self):
        for self_obj in self:
            if self_obj.state == 'cancel':
                self_obj.state = 'draft'

    @api.multi
    def rectificate_invoice(self):
        for self_obj in self:

            type_refund = 'in_refund'
            compose_form = self.env.ref(
                'easy_invoice.easy_invoice_supplier_form', False)
            if self_obj.type == 'out_invoice':
                compose_form = self.env.ref(
                    'easy_invoice.easy_invoice_customer_form', False)
                type_refund = 'out_refund'

            vals = {
                'type': type_refund,
                'state': 'draft',
                'partner_id':    self_obj.partner_id.id,
                'company_id': self_obj.company_id.id,
                'rectificative_invoice_id': self_obj.id,
                'date_invoice': fields.Date.today(),
                'date_expiration': fields.Date.today(),
                'configuration_sequence_id': self_obj.configuration_sequence_id.id,

            }
            invoice_created = self.env['easy.invoice'].create(vals)
            self_obj.easy_invoice_id = invoice_created.id
            for line_obj in self_obj.invoice_line_ids:
                vals = {
                    'invoice_id': invoice_created.id,
                    'name': line_obj.name,
                    'price_unit': line_obj.price_unit,
                    'uom_id':    line_obj.uom_id.id,
                    'product_id': line_obj.product_id.id,
                    'quantity': line_obj.quantity,
                    'currency_id': line_obj.currency_id.id,
                    'company_id': line_obj.company_id.id,
                }
                invoice_line_created = self.env[
                    'easy.invoice.line'].create(vals)

            if invoice_created:
                return {
                    'name': _('Rectificative'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'easy.invoice',
                    'res_id': invoice_created.id,
                    'views': [(compose_form.id, 'form')],
                    'view_id': compose_form.id,
                    'context': {},
                }
            return invoice_created

    @api.multi
    def cancel_invoice(self):
        for self_obj in self:
            for line_obj in self_obj.payment_line_ids:

                if line_obj.id != self_obj.invoice_residual_amount_id.id:
                    raise ValidationError(
                        _('You cant not Cancel a Invoice with Payments. First Cancel all Payments and back to Cancel the Invoice.'))
        self.state = 'cancel'
        self_obj.invoice_residual_amount_id.unlink()

    # @api.model
    # def create(self, vals):
    #     onchanges = {
    #         # '_onchange_partner_id': ['account_id', 'payment_term_id', 'fiscal_position_id', 'partner_bank_id'],
    #         # '_onchange_journal_id': ['currency_id'],
    #     }
    #     for onchange_method, changed_fields in onchanges.items():
    #         if any(f not in vals for f in changed_fields):
    #             invoice = self.new(vals)
    #             getattr(invoice, onchange_method)()
    #             for field in changed_fields:
    #                 if field not in vals and invoice[field]:
    #                     vals[field] = invoice._fields[
    #                         field].convert_to_write(invoice[field], invoice)
    #     invoice = super(EasyInvoice, self.with_context(
    #         mail_create_nolog=True)).create(vals)
    #     return invoice

    @api.multi
    def print_easyinvoice(self):
        return self.env.ref('easy_invoice.action_report_easyinvoice').report_action(self)

    @api.multi
    def print_easyshipment(self):
        return self.env.ref('easy_invoice.action_report_easyshipment').report_action(self)

    @api.multi
    def get_server_datetime(self):
        user = self.env['res.users'].browse(self.env.uid)
        tz = pytz.timezone(user.tz) if user.tz else pytz.utc
        return fields.datetime.now(tz).strftime("%d/%m/%y %H:%M:%S")

    @api.multi
    def pay(self):
        values = {
            'partner_id': self.partner_id.id,
            'group_type': 'out_group',
            'state': 'draft',
            'out_invoice_ids': [(0, 0, {'invoice_id': self.id,
                                        'amount2pay': self.amount_total,
                                        'currency_id': self.currency_id.id,
                                        })],
        }
        payment_group_id = self.env['easy.payment.group'].create(values)
        view_id = self.env.ref('easy_invoice.easy_payment_out_group_form').id
        return {
            'name': _('New'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'easy.payment.group',
            'view_id': view_id,
            'res_id': payment_group_id.id,
            'target': 'target',
            'type': 'ir.actions.act_window',
        }
