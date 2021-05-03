from odoo import models, api, fields, _


class EasyEmployeeCC(models.Model):
    _inherit = "easy.employee.cc"

# Fields
    analytic_line_id = fields.Many2one('account.analytic.line',
                                       'Analytic Line Move')
    analytic_account_id = fields.Many2one('account.analytic.account',
                                          'Analytic Account',
                                          related='analytic_line_id.account_id'
                                          )
# end Fields
    @api.multi
    def create_movement(self, ttype, amount, employee_obj, description,
                        recaudation_id, date, date_contable):
        easy_employee_cc_obj = super(EasyEmployeeCC, self).\
            create_movement(ttype, amount, employee_obj, description,
                            recaudation_id, date, date_contable)
        if easy_employee_cc_obj:
            if employee_obj and employee_obj.analytic_account_id:
                self.create_line_analytic_account_line(easy_employee_cc_obj)
        return easy_employee_cc_obj

    @api.multi
    def create_line_analytic_account_line(self, easy_employee_cc_obj,
                                          analytic=None):
        if easy_employee_cc_obj:
            analytic_account_obj = easy_employee_cc_obj.employee_id.\
                analytic_account_id
            if analytic:
                analytic_account_obj = analytic
                easy_employee_cc_obj.analytic_account_id =\
                    analytic_account_obj.id
            amount = 0.0
            if easy_employee_cc_obj.\
                    easy_employe_cc_settlement_id.ttype == 'haberes':
                amount = easy_employee_cc_obj.amount_salary if\
                    easy_employee_cc_obj.easy_employe_cc_settlement_id.symbol\
                    == "sum" else -(easy_employee_cc_obj.amount_advancement)
            else:
                return True
            vals = {
                'name': easy_employee_cc_obj.employee_id.name + ':' +
                easy_employee_cc_obj.easy_employe_cc_settlement_id.name
                + ': ' + easy_employee_cc_obj.description,
                'account_id': analytic_account_obj.id,
                'product_id': easy_employee_cc_obj.employee_id.product_id.id,
                'unit_amount': 1,
                'user_id': self.env.user.id,
                'company_id': self.env['res.company']._company_default_get
                ('easy.invoice.analytic.realation').id,
                'date': easy_employee_cc_obj.date_contable,
                'employee_cc_id': easy_employee_cc_obj.id,
                'amount': amount * (-1.0),
            }
            line_created = self.env['account.analytic.line'].create(vals)
            easy_employee_cc_obj.analytic_line_id = line_created.id
            # The following line sends a message for each line created and 
            # this annoys the user because more than one is created per import.
            # self.create_message(easy_employee_cc_obj,analytic_account_obj) 

    @api.multi
    def create_message(self, easy_employee_cc_obj, old):
        # este no esta andando
        # _logger.debug('======>alert_apocryphal<======')
        easy_employee_cc_obj.ensure_one()
        subject = _('Se crea Movimiento Analítico')
        message = _(' con la cuenta Cuenta Analítica ')+_(old.name)
        message += _(' en la linea ')+_(easy_employee_cc_obj.description)
        user_ids = easy_employee_cc_obj.env['res.users'].search([('active',
                                                                '=', True)])
        easy_employee_cc_obj.env['mail.message'].\
            create({'message_type': 'notification',
                    'body': message,
                    'subject': subject,
                    'needaction_partner_ids': [(4, user.partner_id.id, None)
                                               for user in user_ids],
                    'model': 'hr.employee',
                    'res_id': easy_employee_cc_obj.employee_id.id})
