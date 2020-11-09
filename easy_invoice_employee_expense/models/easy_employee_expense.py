# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class EasyEmployeeExpense(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _name = "easy.employee.expense"
    _order = "date desc,id desc"

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id

    @api.depends('invoice_ids.invoice_line_ids')
    def _compute_amount_invoice(self):
        amount_invoice = 0.0
        for invoice_obj in self.invoice_ids:
            amount_invoice += sum(line.price_subtotal for line in invoice_obj.invoice_line_ids)
        self.amount_invoice = amount_invoice

## Fields 
    description = fields.Char(string='Reference/Description',)
    date = fields.Date(string='Date',)
    employee_id = fields.Many2one('hr.employee', string='Payment')
    amount = fields.Monetary(string='Amount',)
    amount_expense = fields.Monetary(string='Amount Expense',)
    amount_invoice = fields.Monetary(string='Amount Invoice',compute='_compute_amount_invoice')
    amount_returned = fields.Monetary(string='Amount Returned',)
    recaudation_id = fields.Many2one('easy.recaudation', string='Recaudation Related')

    currency_id = fields.Many2one('res.currency', string='Currency',required=True, readonly=True, default=_default_currency,)
    payment_amount_id = fields.Many2one('easy.payment', string='Payment Related')
    payment_invoice_id = fields.Many2one('easy.payment', string='Payment Related')
    payment_returned_id = fields.Many2one('easy.payment', string='Payment Related')

    invoice_ids = fields.One2many('easy.invoice', 'expense_id', string='Invoices')
 
    state = fields.Selection([('draft','Draft'),              
                              ('pending_rendig','Pending to Rendig'),              
                              ('rendig','Rendig'),    
                             ], string="State",default='draft')
## end Fields 
    @api.multi
    def confirm(self):
        ###########
        # crear la linea de movimiento en la caja con el valor "amount" y cambiar de estado
        ###########
        for rec in self:
            if rec.amount<=0.0:
                raise ValidationError(_('You cannot Confirm an Expense with a negative or cero Total Amount.'))
    
            rec.payment_amount_id = rec.create_move_retire().id
            rec.amount_expense = rec.amount
            rec.state = 'pending_rendig'



    @api.multi
    def rendig(self):
        ###########
        # Variables:
            # amount_expense es el gasto que se "perdio" sin rendicion (remis, subte, plata gastada sin comprobante para ingresas al sistema)
            #     no se hace mas nada con este dinero
            # amount_invoice es el gasto que se produce con una factura para ingresar al sistema (compra de insumo,materiales, etc)
            #     DEBE esto "devuelve" el dinero a la caja para que posterior mente se creen las factuaras pertinentes y "retire" el dinero
            #      crearse en las facturas 
            # amount_reurned es el efectivo que el empleado DEVUELVE en dinero a la caja debe crearse una linea de ingreso en la caja
            # la suma de los 3 tiene que ser igual al valor en "amount", 
        ###########
        for rec in self:
            rec.amount_expense = rec.amount - rec.amount_invoice - rec.amount_returned
            if rec.amount_expense<0.0:
                raise ValidationError(_('You cannot Confirm an Expense with a negative or cero Expense Amount.'))

            if rec.amount_invoice<0.0:
                raise ValidationError(_('You cannot Confirm an Expense with a negative or cero Invoice Amount.'))

            if rec.amount_returned<0.0:
                raise ValidationError(_('You cannot Confirm an Expense with a negative or cero Returned Amount.'))

            if rec.amount_invoice != 0.0:
                rec.payment_invoice_id = rec.create_move_deposit(rec.amount_invoice).id
                for invoice_obj in rec.invoice_ids:
                    vals = {
                        'state' : 'draft',
                        'partner_id' : invoice_obj.partner_id.id,
                        #'currency_id' : fields.Many2one('res.currency', string:'Currency')
                        'date' : rec.date,
                        'recaudation_id': rec.recaudation_id.id ,   
                        'group_type':'in_group', 
                    }
                    group_create_obj = rec.env['easy.payment.group'].create(vals)  
                    #aux_amount2pay = invoice_obj.residual_amount
                    vals = {
                            'invoice_id' : invoice_obj.id,
                            'partner_id' : invoice_obj.partner_id.id,
                            #'currency_id' : fields.Many2one('res.currency', string:'Currency')
                            'amount2pay' : invoice_obj.residual_amount,
                            'in_invoice_group_id': group_create_obj.id   ,    
                            }
                    group_line_create_obj = self.env['easy.payment.group.line'].create(vals) 
                    group_create_obj.control_amount()
                    group_create_obj.draft2prepared()
                    group_create_obj.prepared2processed()

            if rec.amount_returned != 0.0:
                rec.payment_returned_id = rec.create_move_deposit(rec.amount_returned+rec.amount_expense).id

            if rec.amount_expense != 0.0:
                rec.payment_returned_id = rec.create_move_retire(amount2pay=rec.amount_expense).id
            
            rec.state = 'rendig'
            return rec

    @api.multi
    def create_move_deposit(self,amount2pay):
        for rec in self:
            recaudation_obj = rec.recaudation_id
            amount_total =  amount2pay
            sequence_number = ''
            state = 'deposit' 
            sequence_number = recaudation_obj.configuration_sequence_id.recaudation_deposit_sequence_id.next_by_id()
            
            vals = {
                'name': rec.description,
                'type': state,
                #'invoice_id': self_obj.id ,
                'amount_total':  amount_total,

                'amount_in': 0.0,
                'amount_out':  amount_total,

                #'amount_residual': self_obj.amount_total,
                'recaudation_id':   recaudation_obj.id ,
                #'payed_id': self_obj.recaudation_id   ,
                'date_pay': rec.date   ,  
                'sequence_number': sequence_number,  

            }
            line_created = self.env['easy.payment'].create(vals) 
            #rec.payment_id = line_created.id
            #rec.state = 'pending_rendig'
        return line_created


    @api.multi
    def create_move_retire(self,amount2pay=None):
        for rec in self:
            recaudation_obj = rec.recaudation_id
            amount_total = rec.amount
            if amount2pay:
                amount_total = amount2pay
            sequence_number = ''
            state = 'retire'
            recaudation_obj.subtract(amount_total)
            sequence_number = recaudation_obj.configuration_sequence_id.recaudation_retire_sequence_id.next_by_id()
            
            vals = {
                'name': rec.description,
                'type': state,
                #'invoice_id': self_obj.id ,
                'amount_total':  amount_total * (-1.0),

                'amount_in': amount_total ,
                'amount_out': 0.0,

                #'amount_residual': self_obj.amount_total,
                'recaudation_id':   recaudation_obj.id ,
                #'payed_id': self_obj.recaudation_id   ,
                'date_pay': rec.date   ,  
                'sequence_number': sequence_number,  

            }
            line_created = self.env['easy.payment'].create(vals) 
            #rec.payment_id = line_created.id
            #rec.state = 'pending_rendig'
        return line_created
    
 












































    @api.multi
    def create_recaudation_move(self,amount2pay=0.0):
        for rec in self:
            recaudation_obj = rec.recaudation_id

            amount_total =  rec.amount_salary + rec.amount_advancement
            if amount2pay != 0.0:
                amount_total = amount2pay

            sequence_number = ''
            state = 'retire'
            if rec.type == 'salary': 
                if not recaudation_obj.boolean_permit_amount_negative and recaudation_obj.amount_box - amount_total < 0.0:
                    raise ValidationError(_('You can not Retire without Funds. Make a Transference or permit movement in negative Amount'))
                amount_total = amount_total * (-1.0)
                sequence_number = recaudation_obj.configuration_sequence_id.recaudation_retire_sequence_id.next_by_id()
            if rec.type == 'advancement':
                if not recaudation_obj.boolean_permit_amount_negative and recaudation_obj.amount_box - amount_total < 0.0:
                    raise ValidationError(_('You can not Retire without Funds. Make a Transference or permit movement in negative Amount'))
                amount_total = amount_total * (-1.0)
                sequence_number = recaudation_obj.configuration_sequence_id.recaudation_retire_sequence_id.next_by_id()   
            
            vals = {
                'name': rec.description,
                'state': state,
                #'invoice_id': self_obj.id ,
                'amount_total':  amount_total,

                'amount_in': amount_total,
                'amount_out': 0.0,

                #'amount_residual': self_obj.amount_total,
                'recaudation_id':   recaudation_obj.id ,
                #'payed_id': self_obj.recaudation_id   ,
                'date_pay': rec.date   ,  
                'sequence_number': sequence_number,  

            }
            line_created = self.env['easy.payment'].create(vals) 
            rec.payment_id = line_created.id
            #rec.state = 'pending_rendig'
        return line_created