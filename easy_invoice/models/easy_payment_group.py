from odoo import api, exceptions, fields, models, _
from odoo.tools import float_is_zero, float_compare, pycompat
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


class EasyPaymentGroup(models.Model):

    _name = "easy.payment.group"
    _description = "Easy Payment Group"
    _order = "date desc,name desc"

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id


# Fields
    name = fields.Char(string='Name', default='Borrador')
    partner_id = fields.Many2one('res.partner', string='Partner')
    currency_id = fields.Many2one(
        'res.currency', string='Currency', default=_default_currency)
    date = fields.Date(string='Date', default=lambda o: fields.Date.today())
    user_id = fields.Many2one('res.users', string='Salesperson', track_visibility='onchange',
                              readonly=True, states={'draft': [('readonly', False)]},
                              default=lambda self: self.env.user, copy=False)

    amount_total_debt = fields.Monetary(
        string='Amount Total Debt', )  # compute='control_amount',
    amount_total_rectificative = fields.Monetary(
        string='Amount Total Rectificative', )  # compute='control_amount',
    # compute='control_amount',
    amount2pay = fields.Monetary(string='Amount To Pay', )
    amount_money = fields.Monetary(
        string='Amount Money', )  # compute='control_amount',
    amount_money_defined = fields.Monetary(
        string='Amount Money Defined', )  # compute='control_amount',

    group_type = fields.Selection([('in_group', 'In Group'),
                                   ('out_group', 'Out Group'),
                                   ], string='Group Type')
    state = fields.Selection([('draft', 'Draft'),
                              ('prepared', 'Prepared'),
                              ('processed', 'Processed'),
                              ('cancel', 'Cancel'),
                              ], string='State', default='draft')

    in_invoice_ids = fields.One2many(
        'easy.payment.group.line', 'in_invoice_group_id', string='Invoice')
    in_rectificative_ids = fields.One2many(
        'easy.payment.group.line', 'in_rectificative_group_id', string='Rectificative', )

    out_invoice_ids = fields.One2many(
        'easy.payment.group.line', 'out_invoice_group_id', string='Invoice')
    out_rectificative_ids = fields.One2many(
        'easy.payment.group.line', 'out_rectificative_group_id', string='Rectificative', )

# ends Field    </tree>

    @api.onchange('partner_id')
    def onchange_partner_id(self):

        # borrando los que ya tiene

        in_invoice_ids = []
        in_rectificative_ids = []
        out_invoice_ids = []
        out_rectificative_ids = []

        # Agredando todas las deudas que tenga
        for invoice_obj in self.env['easy.invoice'].search([('partner_id', '=', self.partner_id.id), ('state', '=', 'open')], order="date_invoice"):
            if self.group_type == 'in_group':
                if invoice_obj.type == 'in_invoice':
                    vals = {
                        'invoice_id': invoice_obj.id,
                        'partner_id': self.partner_id.id,
                        'residual_amount': invoice_obj.residual_amount,
                        'amount2pay': invoice_obj.residual_amount,
                    }
                    in_invoice_ids.append(vals)
                if invoice_obj.type == 'in_refund':
                    vals = {
                        'invoice_id': invoice_obj.id,
                        'partner_id': self.partner_id.id,
                        'residual_amount': invoice_obj.residual_amount,
                        'amount2pay': invoice_obj.residual_amount,
                    }
                    in_rectificative_ids.append(vals)

            if self.group_type == 'out_group':
                if invoice_obj.type == 'out_invoice':
                    vals = {
                        'invoice_id': invoice_obj.id,
                        'partner_id': self.partner_id.id,
                        'residual_amount': invoice_obj.residual_amount,
                        'amount2pay': invoice_obj.residual_amount,
                    }
                    out_invoice_ids.append(vals)
                if invoice_obj.type == 'out_refund':
                    vals = {
                        'invoice_id': invoice_obj.id,
                        'partner_id': self.partner_id.id,
                        'residual_amount': invoice_obj.residual_amount,
                        'amount2pay': invoice_obj.residual_amount,
                    }
                    out_rectificative_ids.append(vals)

        self.in_invoice_ids = False
        self.in_rectificative_ids = False
        self.out_invoice_ids = False
        self.out_rectificative_ids = False
        self.in_invoice_ids = in_invoice_ids
        self.in_rectificative_ids = in_rectificative_ids
        self.out_invoice_ids = out_invoice_ids
        self.out_rectificative_ids = out_rectificative_ids

    @api.multi
    def cancel2draft(self):
        self.state = 'draft'

    @api.multi
    def processed2cancel(self):
        self.state = 'cancel'

    @api.multi
    def draft2prepared(self):
        self.control_amount()
        if self.name == 'Borrador':
            self.name = 'Preparado'
        self.state = 'prepared'

    @api.multi
    def prepared2draft(self):
        self.name = 'Borrador'
        self.state = 'draft'

    @api.multi
    def prepared2processed(self):
        raise ValidationError(_('Not implemented Yet.'))
        self.name = 'Procesado'
        self.state = 'processed'

    @api.multi
    def sum_amount_money_defined(self, amount_total_rectificative):
        # este metodo se agrega exclusivamente para dejar abierto para agregar el monto de saldo
        #   deudor o acreedor del partner al calculo
        return amount_total_rectificative

    @api.multi
    def _control_rectificative_ids(self, rectificative_ids):

        for rec in self:
            amount_total_rectificative = 0.0
            if_invoice_ids = {}
            for line_obj in rectificative_ids:
                line_obj.residual_amount = line_obj.invoice_id.residual_amount
                if not str(line_obj.invoice_id.id) in if_invoice_ids:
                    if_invoice_ids[str(line_obj.invoice_id.id)
                                   ] = line_obj.invoice_id
                else:
                    raise ValidationError(
                        'No se puede agregar 2 veces una Rectificativa (Ref: %s)') % str(line_obj.name)
                if line_obj.residual_amount <= line_obj.amount2pay:
                    line_obj.amount2pay = line_obj.residual_amount
                amount_total_rectificative += line_obj.amount2pay

        return (if_invoice_ids, rectificative_ids, amount_total_rectificative)

    @api.multi
    def control_amount(self):
        for rec in self:
            if rec:  # .state != 'processed':
                amount_total_debt = 0.0
                amount2pay = 0.0
                amount_money_defined = rec.amount_money_defined
                amount_total_rectificative = 0.0

                invoice_ids = []
                rectificative_ids = []
                if rec:

                    # busco que variables usar
                    if rec.group_type and rec.group_type in ('in_group'):
                        invoice_ids = rec.in_invoice_ids
                        rectificative_ids = rec.in_rectificative_ids
                    if rec.group_type and rec.group_type in ('out_group'):
                        invoice_ids = rec.out_invoice_ids
                        rectificative_ids = rec.out_rectificative_ids

                    # recorro las rectificativas
                    if_invoice_ids, rectificative_ids, amount_total_rectificative = self._control_rectificative_ids(
                        rectificative_ids)

                    flag_amount_defined = False
                    # busco si setea algo de dinero con el cual pagar
                    if amount_money_defined != 0.0:
                        flag_amount_defined = True
                        amount_money_defined += self.sum_amount_money_defined(
                            amount_total_rectificative)
                    else:
                        self.sum_amount_money_defined(
                            amount_total_rectificative)

                    # recorro las facturas y distribuyo el dinero que va a
                    # pagar
                    for line_obj in invoice_ids:
                        line_obj.residual_amount = line_obj.invoice_id.residual_amount
                        if not str(line_obj.invoice_id.id) in if_invoice_ids:
                            if_invoice_ids[
                                str(line_obj.invoice_id.id)] = line_obj.invoice_id
                        else:
                            raise ValidationError('No se puede agregar 2 veces una Factura (Ref: %s)' % str(
                                line_obj.invoice_id.name))
                        amount_total_debt += line_obj.residual_amount
                        if not flag_amount_defined:
                            amount2pay += line_obj.amount2pay
                        else:
                            if amount_money_defined >= line_obj.residual_amount:
                                line_obj.amount2pay = line_obj.residual_amount
                                amount2pay += line_obj.amount2pay
                                amount_money_defined -= line_obj.amount2pay
                            else:
                                line_obj.amount2pay = amount_money_defined
                                amount_money_defined = 0.0
                                amount2pay += line_obj.amount2pay

                        line_obj.amount2payed = line_obj.amount2pay

                rec.amount_total_debt = amount_total_debt
                rec.amount2pay = amount2pay
                rec.amount_total_rectificative = amount_total_rectificative
                rec.amount_money = amount2pay - amount_total_rectificative

            if rec.amount_money < 0.0:
                raise ValidationError(
                    _('You cant not Prepare a Group with Amount Money in 0 or Negative.-'))

    @api.multi
    def print_easypayment(self):
        return self.env.ref('easy_invoice.action_report_easy_paymentgroup').report_action(self)


#     @api.multi
#     def control_amount(self):
#         for rec in self:
#             if rec and rec.state == 'draft':#.state != 'processed':
#                 amount_total_debt = 0.0
#                 amount2pay = 0.0
#                 amount_money_defined = rec.amount_money_defined
#                 amount_total_rectificative = 0.0

#                 invoice_ids = []
#                 rectificative_ids = []

#                 # busco que variables usar
#                 if rec.group_type and rec.group_type in ('in_group'):
#                     invoice_ids = rec.in_invoice_ids
#                     rectificative_ids = rec.in_rectificative_ids
#                 if rec.group_type and rec.group_type in ('out_group'):
#                     invoice_ids = rec.out_invoice_ids
#                     rectificative_ids = rec.out_rectificative_ids

#                 # recorro las rectificativas
#                 if_invoice_ids,rectificative_ids,amount_total_rectificative = self._control_rectificative_ids(rectificative_ids)

# ## si viene un monto  < 0.00 USAR SOLO LAS NOTAS DE CREDITO Y EL SALGO DEL CLIENTE
# ## si viene un monto == 0.00 usar NOTAS DE CREDITO, MONTO DE CLIENTE y pagar TODO EL RESTO de las facturas
# ## si viene un monto  > 0.00  usar notas de credito, monto de cliente y EL TOTAL DEL MONTO A PAGAR
#                 flag_amount_not_defined = True
#                 # busco si setea algo de dinero con el cual pagar
#                 if amount_money_defined > 0.009:
#                     amount_money_defined += self._sum_amount_money_defined(amount_total_rectificative)
#                 else:
#                     #if amount_money_defined <= 0.009 and amount_money_defined >= -0.009:
#                     flag_amount_not_defined = False
#                     amount_money_defined = self._sum_amount_money_defined(amount_total_rectificative)
#                     #else:
#                         #if amount_money_defined < -0.009:
#                             #amount_money_defined = self._sum_amount_money_defined(amount_total_rectificative)
# ## hacer que esto calcule bien como quiero y pienso..
#                 #recorro las facturas y distribuyo el dinero que va a pagar
#                 for line_obj in invoice_ids:
#                     line_obj.residual_amount = line_obj.invoice_id.residual_amount
#                     if not str(line_obj.invoice_id.id) in if_invoice_ids:
#                         if_invoice_ids[str(line_obj.invoice_id.id)] = line_obj.invoice_id
#                     else:
#                         raise ValidationError('No se puede agregar 2 veces una Factura (Ref: %s)'%str(line_obj.invoice_id.name))

#                     amount_total_debt += line_obj.residual_amount
#                     if flag_amount_not_defined:
#                         amount2pay += line_obj.amount2pay
#                     else:
#                         if amount_money_defined >= line_obj.residual_amount:
#                             line_obj.amount2pay = line_obj.residual_amount
#                             amount2pay += line_obj.amount2pay
#                             amount_money_defined -= line_obj.amount2pay
#                         else:
#                             line_obj.amount2pay = amount_money_defined
#                             amount_money_defined = 0.0
#                             amount2pay += line_obj.amount2pay
#                     line_obj.amount2payed = line_obj.amount2pay
# ## setear correctamente estas variables  la variable amount2pay tiene que terminar en cero para queno cree pagos en la caja

#                 rec.amount_money_defined =  amount_money_defined
#                 rec.amount_total_debt = amount_total_debt
#                 rec.amount2pay = amount2pay
#                 rec.amount_total_rectificative = amount_total_rectificative
#                 rec.amount_money = amount2pay - amount_total_rectificative

#             if rec.amount_money < 0.0:
#                 raise ValidationError(_('You cant not Prepare a Group with Amount Money in 0 or Negative.-'))


#     @api.onchange('partner_id')
#     def onchange_partner_id(self):
#         # borrando los que ya tiene
#         in_invoice_ids =[]
#         in_rectificative_ids =[]
#         out_invoice_ids =[]
#         out_rectificative_ids =[]
#         amount_total_debt = 0.0
#         amount_total_rectificative = 0.0
#         # Agredando todas las deudas que tenga
#         for invoice_obj in self.env['easy.invoice'].search([('partner_id', '=', self.partner_id.id), ('state', '=', 'open')],order="date_invoice"):
#             if self.group_type == 'in_group':
#                 if invoice_obj.type == 'in_invoice':
#                     vals = {
#                         'invoice_id': invoice_obj.id,
#                         'partner_id': self.partner_id.id,
#                         'residual_amount': invoice_obj.residual_amount,
#                         'amount2pay': invoice_obj.residual_amount,
#                     }
#                     in_invoice_ids.append(vals)
#                     amount_total_debt +=invoice_obj.residual_amount
#                 if invoice_obj.type == 'in_refund':
#                     vals = {
#                         'invoice_id': invoice_obj.id,
#                         'partner_id': self.partner_id.id,
#                         'residual_amount': invoice_obj.residual_amount,
#                         'amount2pay': invoice_obj.residual_amount,
#                     }
#                     in_rectificative_ids.append(vals)
#                     amount_total_rectificative +=invoice_obj.residual_amount

#             if self.group_type == 'out_group':
#                 if invoice_obj.type == 'out_invoice':
#                     vals = {
#                         'invoice_id': invoice_obj.id,
#                         'partner_id': self.partner_id.id,
#                         'residual_amount': invoice_obj.residual_amount,
#                         'amount2pay': invoice_obj.residual_amount,
#                     }
#                     out_invoice_ids.append(vals)
#                     amount_total_debt +=invoice_obj.residual_amount
#                 if invoice_obj.type == 'out_refund':
#                     vals = {
#                         'invoice_id': invoice_obj.id,
#                         'partner_id': self.partner_id.id,
#                         'residual_amount': invoice_obj.residual_amount,
#                         'amount2pay': invoice_obj.residual_amount,
#                     }
#                     out_rectificative_ids.append(vals)
#                     amount_total_rectificative +=invoice_obj.residual_amount

#         self.in_invoice_ids = False
#         self.in_rectificative_ids = False
#         self.out_invoice_ids = False
#         self.out_rectificative_ids = False

#         #self.write({'in_invoice_ids': [(6, 0, in_invoice_ids)]})
#         #self.write({'in_rectificative_ids': [(6, 0, in_rectificative_ids)]})
#         #self.write({'out_invoice_ids': [(6, 0, out_invoice_ids)]})
#         #self.write({'out_rectificative_ids': [(6, 0, out_rectificative_ids)]})

#         self.in_invoice_ids = in_invoice_ids
#         self.in_rectificative_ids = in_rectificative_ids
#         self.out_invoice_ids = out_invoice_ids
#         self.out_rectificative_ids = out_rectificative_ids

#         self.amount_total_debt = amount_total_debt
#         self.amount2pay = amount_total_debt
#         self.amount_total_rectificative = amount_total_rectificative


#         #self.partner_amount = self.partner_id.amount_anticipe
#         #self.write({'name' : 'Borrador'})


#     @api.multi
#     def cancel2draft(self):
#         self.state = 'draft'

#     @api.multi
#     def processed2cancel(self):
#         self.state = 'cancel'

#     @api.multi
#     def draft2prepared(self):
#         self.control_amount()
#         if self.name == 'Borrador':
#             self.name = 'Preparado'
#         self.state = 'prepared'

#     @api.multi
#     def prepared2draft(self):
#         self.amount_money_defined = 0.0
#         self.name = 'Borrador'
#         self.state = 'draft'

#     @api.multi
#     def prepared2processed(self):
#         raise ValidationError(_('Not implemented Yet.'))
#         self.name = 'Procesado'
#         self.state = 'processed'


#     @api.multi
#     def _sum_amount_money_defined(self,amount_total_rectificative):
#         # este metodo se agrega exclusivamente para dejar abierto para agregar el monto de saldo
#         #   deudor o acreedor del partner al calculo
#         return  amount_total_rectificative


#     @api.multi
#     def _control_rectificative_ids(self,rectificative_ids):

#         for rec in self:
#             amount_total_rectificative = 0.0
#             if_invoice_ids = {}
#             for line_obj in rectificative_ids:
#                 line_obj.residual_amount = line_obj.invoice_id.residual_amount
#                 if not str(line_obj.invoice_id.id) in if_invoice_ids:
#                     if_invoice_ids[str(line_obj.invoice_id.id)] = line_obj.invoice_id
#                 else:
#                     raise ValidationError('No se puede agregar 2 veces una Rectificativa (Ref: %s)')%str(line_obj.name)
#                 if line_obj.residual_amount <= line_obj.amount2pay:
#                     line_obj.amount2pay = line_obj.residual_amount
#                 amount_total_rectificative += line_obj.amount2pay

#         return (if_invoice_ids,rectificative_ids,amount_total_rectificative)

#     @api.multi
#     def print_easypayment(self):
# return
# self.env.ref('easy_invoice.action_report_easy_paymentgroup').report_action(self)
