# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _

class EasyInvoiceLine(models.Model):
    _inherit = "easy.invoice.line"






    @api.multi
    def edit_analytic_line(self,analytic_account_id):
        for self_obj in self:
            if self_obj.analytic_line_id:
                self.edit_message(self_obj.analytic_line_id.account_id,analytic_account_id)
                self_obj.analytic_account_id = analytic_account_id
                self_obj.analytic_line_id.account_id = analytic_account_id
            else:
                self.create_line_analytic_account_line(analytic = analytic_account_id)
                
        return True

    @api.multi
    def edit_message(self,old,new): # este no esta andando
        #_logger.debug('======>alert_apocryphal<======')
        self.ensure_one()
        subject = _('Edicion de Cuentas Analíticas ')
        message = _('Se Cambió la Cuenta Analítica ')+_(old.name) 
        message += _(' por ')+_(new.name)
        message += _(' en la linea ')+_(self.name)
        user_ids = self.env['res.users'].search([('active','=',True)])

        self.env['mail.message'].create({'message_type':'notification',
                                         'body': message,
                                         'subject': subject,
                                         'needaction_partner_ids': [(4, user.partner_id.id, None) for user in user_ids],   
                                         'model': 'easy.invoice',
                                         'res_id': self.invoice_id.id,})
    

