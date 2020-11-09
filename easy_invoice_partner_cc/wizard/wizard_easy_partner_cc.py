from odoo import models, api, fields, _
from ast import literal_eval
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class WizardEasyPartnerCc(models.TransientModel):

    _name = 'wizard.easy.partner.cc'
    _description = 'Wizard Easy partner Anticipe/Advancement'

### Fields
    name = fields.Text(string='Description')
    amount = fields.Float(string='Amount', )
    date = fields.Date(string='Date',default=fields.Date.today )
    partner_id = fields.Many2one('res.partner', string='Partner')
    #customer = fields.Boolean(string='customer', )
    #supplier = fields.Boolean(string='supplier', )
    recaudation_id = fields.Many2one('easy.recaudation', string='Recaudation')
    type = fields.Selection([('anticipe', 'Anticipe'),('advancement', 'Advancement')], string='Type',default='anticipe')
### ends Field 


# ANTICIPO de clientes      + haber   anticipe
# ADELANTO a proveedores    + debe    advancement

    @api.multi
    def create_move(self):
        for self_obj in self: 
            line_created_cc = None
            if self_obj.type == 'anticipe':
                if self_obj.amount <=   0.0:
                    raise ValidationError(_('No se pueden realizar Recibos cero o Negativos.'))
                vals = {
                    'description': self_obj.name,
                    'partner_id': self_obj.partner_id.id,
                    'amount_anticipe':  self_obj.amount,
                    'amount_advancement': 0.0,
                    'date': self_obj.date   ,      
                }
                line_created_cc = self.env['easy.partner.cc'].create(vals) 
                line_created_cc.create_recaudation_move(self_obj.recaudation_id, 'deposit')
            if self_obj.type == 'advancement':
                if self_obj.amount <=   0.0:
                    raise ValidationError(_('No se pueden realizar Adelantos cero o Negativos.'))
                vals = {
                    'description': self_obj.name,
                    'partner_id': self_obj.partner_id.id,
                    'amount_anticipe':  0.0 ,
                    'amount_advancement': self_obj.amount,
                    'date': self_obj.date   ,      
                }
                line_created_cc = self.env['easy.partner.cc'].create(vals) 
                line_created_cc.create_recaudation_move(self_obj.recaudation_id,'retire')
            
            actions = []
            actions.append({'type': 'ir.actions.act_window_close'})
            actions.append({'name': _("Imprimir"),
                    'type': 'ir.actions.report',
                    'report_name': 'print_anticipe_advancement',
                    'report_type': 'aeroo',
                    'res_model': 'easy.partner.cc',
                    'report_file': 'easy_invoice_partner_cc/report/print_anticipe_advancement.odt',
                    'tml_source': 'file',
                    'context':{'active_ids': [line_created_cc.id],'active_id': line_created_cc.id}
                    })

            return {
                    'type': 'ir.actions.act_multi',
                    'actions': actions
                }

