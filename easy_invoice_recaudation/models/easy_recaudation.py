from odoo import api, exceptions, fields, models, _
from odoo.tools import float_is_zero, float_compare, pycompat
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class EasyRecaudation(models.Model):

    _name = "easy.recaudation"
    _description = "Easy Recaudation"

### Fields
    name = fields.Char(string='Description', required=True)
    date_from = fields.Date('Date From', )
    date_to = fields.Date('Date To', )
    boolean_permit_amount_negative = fields.Boolean(string='Permit Amount Negative', default=False, )
    amount_box = fields.Float(string='Amount Box',compute='_control_amount_box')
    line_recaudation_ids = fields.One2many('easy.payment', 'recaudation_id', string="Line Recaudation")
    line_history_ids = fields.One2many('easy.payment', 'recaudation_history_id', string="Line Recaudation History")
    line_close_ids = fields.One2many('easy.payment', 'recaudation_close_id', string="Line Recaudation Closes")
    line_transfer_ids = fields.One2many('easy.payment', 'recaudation_transfer_id', string="Line Recandation Transfer")
    payment_group_ids = fields.One2many('easy.payment.group', 'recaudation_id', string="Payment Group")
    state = fields.Selection([('draft', 'Draft'),('open', 'Open'),('close', 'Close')], string='State',default='draft')
    configuration_sequence_id = fields.Many2one('easy.sequence',  string="Configuration Sequence", ondelete='restrict')
    user_create_id = fields.Many2one('res.users',  string="User Create")
    user_ids = fields.Many2many('res.users', relation='ease_recaudation_user_rel', column1='easy_recaudation_id',column2='user_id', string="Assigned Users")

### ends Field  
    #,compute='_control_amount_box'
    @api.multi
    @api.depends('line_recaudation_ids.amount_in','line_recaudation_ids.amount_out')
    def _control_amount_box(self):
        for rec in self:
            amount_box = 0.0
            for line_obj in rec.line_recaudation_ids:
                if line_obj.state == 'open':
                    amount_box +=  line_obj.amount_out - line_obj.amount_in
            rec.amount_box = amount_box


    @api.multi
    def partial_close_wizard(self):
        self.ensure_one()
        compose_form = self.env.ref('easy_invoice_recaudation.view_easy_recaudation_close_form', False)
        return {
            'name': _('Partial Close'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'easy.recaudation.close',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': self._context,
        }

    @api.multi
    def partial_close(self, difference, reason):
        for self_obj in self: 
            aux_in = 0.0
            aux_out = 0.0
            for line_obj in self_obj.line_recaudation_ids: 
                if line_obj.type == 'arch':
                    line_obj.recaudation_close_id = self_obj.id
                else:
                    line_obj.recaudation_history_id = self_obj.id

                line_obj.recaudation_id = None
                if line_obj.state == 'open':
                    aux_in += line_obj.amount_in
                    aux_out += line_obj.amount_out
            vals = {
                'name': _('Arqueo de Caja'),
                'amount_in': aux_in,
                'amount_out': aux_out,
                'amount_total': aux_out-aux_in,
                'recaudation_id': self_obj.id, 
                'date_pay': fields.Date.today()  , 
                'type': 'arch'  ,
                'state':'pending'     
            }
            line_created = self.env['easy.payment'].create(vals)
            if difference!=0:
                if difference>0:
                    aux_out=difference
                    aux_in=0.0
                else:
                    aux_in=-difference
                    aux_out=0.0
                
                vals = {
                    'name': _('Ajuste de Caja: (%s)'%(reason)),
                    'amount_in': aux_in,
                    'amount_out': aux_out,
                    'amount_total': aux_out-aux_in,
                    'recaudation_id': self_obj.id, 
                    'date_pay': fields.Date.today()  , 
                    'type': 'arch'  ,
                    'state': 'pending'   
                }
                line_created = self.env['easy.payment'].create(vals) 


    @api.multi
    def draft2open(self):
        for self_obj in self: 
            self_obj.state = 'open'

    @api.multi
    def open2close(self):
        for self_obj in self:
            if not self_obj.date_to:
                raise Warning(_('You can not close a Recaudation without "Date To".'))
            self_obj.state = 'close'

    @api.multi
    def add(self, amount):
        for self_obj in self: 
            print(' va a sumar el monto?')
            print(self_obj.amount_box+amount)
            #self_obj.amount_box=self_obj.amount_box+amount

    @api.multi
    def subtract(self, amount):
        for self_obj in self: 
            if not self_obj.boolean_permit_amount_negative and self_obj.amount_box - amount < 0.0:
                raise ValidationError(_('You cant not Retire without Funds'))
            print(' va a RESTAR el monto?')
            print(self_obj.amount_box-amount)
            #self_obj.amount_box=self_obj.amount_box-amount


   # @api.multi 
   # def unlink(self):
   #  for record in self:
   #    if not record.vente or not record.vente2:
   #       raise osv.except_osv(('Invalid Action!'), ('Le pack est déjà affecté ! Vous ne pouvez pas le supprimer',p.vente2,p.vente))
   #  return super(Pack_Stock, self).unlink()