from odoo import models, api, fields, _
from ast import literal_eval
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class WizardEditCenterCost(models.TransientModel):

    _name = 'wizard.edit.cost.center'
    _description = 'Wizard Edit Cost Center'

### Fields
    cost_center_id = fields.Many2one('cost.center', string='Cost Center')
### ends Field 

    @api.multi
    def edit_cost_center(self):
        for self_obj in self: 
            for ids in self._context['active_ids']:   
                invoice_obj = self.env['easy.invoice'].browse(ids)
                if invoice_obj.cost_center_id:
                    invoice_obj.cost_center_id = self_obj.cost_center_id.id
                    if invoice_obj.cost_center_move_id.cost_center_id:
                        invoice_obj.cost_center_move_id.cost_center_id = self_obj.cost_center_id.id
         