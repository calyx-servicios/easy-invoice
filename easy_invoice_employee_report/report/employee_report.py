# © 2016 Julien Coux (Camptocamp)
# © 2018 Forest and Biomass Romania SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.tools import float_is_zero
from ast import literal_eval
from odoo.exceptions import AccessError, UserError
import logging

_logger = logging.getLogger(__name__)



class EmployeeReport(models.TransientModel):
    """ Here, we just define class fields.
    For methods, go more bottom at this file.

    The class hierarchy is :
    * EmployeeReport

    """

    _name = 'report_employee'
    _inherit = 'account_financial_report_abstract'

    # Filters fields, used for data computation
    date_from = fields.Date()
    date_to = fields.Date()
    company_id = fields.Many2one(
        'res.company',
        index=True
    )
    filter_company_ids = fields.Many2many(comodel_name='res.company')
    filter_account_ids = fields.Many2many(comodel_name='hr.employee')
    # Esto lo dejo para no reescribir todo el codigo nuevamente. 
    # El requerimiento cambio, fue mal especificado y ahora tendria que tirar a la mierda todo el codigo
    #filter_type_ids = fields.Many2many(comodel_name='easy.employee.cc.type')
    filter_settlement_ids = fields.Many2many(comodel_name='easy.employe.cc.settlement')
    filter_settlement_type = fields.Selection(
        [("haberes", "Haberes"), ("pagos_compesacion", "Pagos y Compensaciones")], string="Easy Movement"
    )
    # Data fields, used to browse report data
    type_ids = fields.One2many(
        comodel_name='report_employee_type',
        inverse_name='report_id'
    )


    description = fields.Char(string='Description')
    detail = fields.Boolean(string='Detail')


class EmployeeReportType(models.TransientModel):
    _name = 'report_employee_type'
    _inherit = 'account_financial_report_abstract'
    _order = 'report_id'

    report_id = fields.Many2one(
        comodel_name='report_employee',
        ondelete='cascade',
        index=True
    )

    type = fields.Char()

    type_id = fields.Many2one(
        "easy.employe.cc.settlement", string="Tipo"
    )

    employee_ids = fields.One2many(
        comodel_name='report_employee_employee',
        inverse_name='type_id'
    )


    salary = fields.Float(string='Salary',digits=(16, 2), default=0)
    advancement = fields.Float(string='Advancement',digits=(16, 2), default=0)
    payment = fields.Float(string='Payment',digits=(16, 2), default=0)

    @api.depends('salary', 'advancement','payment')
    def _compute_amount(self):
        for type in self:
            type.total = type.salary-type.advancement-type.payment

    total = fields.Float(digits=(16, 2), string='Amount', compute=_compute_amount)

class EmployeeReportEmployee(models.TransientModel):
    _name = 'report_employee_employee'
    _inherit = 'account_financial_report_abstract'
    _order = 'report_id'

    report_id = fields.Many2one(
        comodel_name='report_employee',
        ondelete='cascade',
        index=True
    )

    employee_id = fields.Many2one(
        'hr.employee',
        index=True
    )
    type_id = fields.Many2one(
        comodel_name='report_employee_type',
        ondelete='cascade',
        index=True
    )
    
    move_ids = fields.One2many(
        comodel_name='report_employee_move',
        inverse_name='employee_id'
    )

    salary = fields.Float(string='Salary',digits=(16, 2), default=0)
    advancement = fields.Float(string='Advancement',digits=(16, 2), default=0)
    payment = fields.Float(string='Payment',digits=(16, 2), default=0)

    

    @api.depends('salary', 'advancement','payment')
    def _compute_amount(self):
        for employee in self:
            employee.total = employee.salary-employee.advancement-employee.payment

    total = fields.Float(digits=(16, 2), string='Amount', compute=_compute_amount)

class CustomerAccountReportMove(models.TransientModel):
    _name = 'report_employee_move'
    _inherit = 'account_financial_report_abstract'

    report_id = fields.Many2one(
        comodel_name='report_employee',
        ondelete='cascade',
        index=True
    )

    employee_id = fields.Many2one(
        comodel_name='report_employee_employee',
        ondelete='cascade',
        index=True
    )
    date = fields.Date()
    description = fields.Char()
    
    salary = fields.Float(string='Salary',digits=(16, 2), default=0)
    advancement = fields.Float(string='Advancement',digits=(16, 2), default=0)
    payment = fields.Float(string='Payment',digits=(16, 2), default=0)

    settlement_type = fields.Selection(
        [("haberes", "Haberes"), ("pagos_compesacion", "Pagos y Compensaciones")], string="Easy Movement"
    )
    settlement_id = fields.Many2one(
        comodel_name='easy.employe.cc.settlement',
        ondelete='cascade',
        index=True
    )

    @api.depends('salary', 'advancement','payment')
    def _compute_amount(self):
        for move in self:
            move.total = move.salary-move.advancement-move.payment
            
    total = fields.Float(digits=(16, 2), string='Amount', compute=_compute_amount)

class EmployeeReportCompute(models.TransientModel):
    """ Here, we just define methods.
    For class fields, go more top at this file.
    """

    _inherit = 'report_employee'

    #####################################################################################
    # This stuff is done to allow flexibility search on description field.
    # Dinamicaly creates a sql domain based on description field and split it by spaces.
    #####################################################################################
    def make_domain(self, domain_name, code):
        domain_code = " and "+domain_name + " ilike  %s "
        if code:
            i = code.find(' ')
            domain_code = ""
            while i != -1:
                domain_code += " and "+domain_name + " ilike  %s "
                code = code[i+1:]
                i = code.find(' ')
            domain_code += " and "+domain_name + " ilike  %s "
        _logger.debug('====> domain_code ====> %s' % domain_code)
        return domain_code

    #####################################################################################
    # Dinamicaly creates the domain insertion parameters for the domain created before!
    #####################################################################################
    def insert_domain(self, domain_name, code):
        domain_code = (code)
        if code:
            i = code.find(' ')
            domain_code = ()
            while i != -1:
                domain_code += ('%'+code[:i]+'%',)
                code = code[i+1:]
                i = code.find(' ')
            domain_code += ('%'+code+'%',)
        _logger.debug(domain_code)
        return domain_code

    def _get_employee_query(self):
        query = """
        SELECT
            cc.employee_id,
            cc.easy_employe_cc_settlement_id as type, 
            hr.name,
            sum(cc.amount_salary) as salary,
            sum(cc.amount_advancement) as advancement, 
            sum(cc.amount_payment) as payment
        FROM easy_employee_cc as cc
            inner join hr_employee hr on cc.employee_id = hr.id
        """
        query += """
        WHERE date between %s and %s
         """
        if self.filter_settlement_ids:
            query += """ and cc.easy_employe_cc_settlement_id in %s """
        if self.filter_account_ids:
            query += """ and cc.employee_id in %s """
        if self.filter_company_ids:
            query += """ and hr.company_id in %s """
        if self.filter_settlement_type:
            query += """ and cc.settlement_type like %s """
        if self.description and len(self.description) > 0:
            query += \
                self.make_domain('cc.description', self.description)
        query += """
        GROUP BY hr.name,cc.employee_id,cc.easy_employe_cc_settlement_id
        ORDER by hr.name
        """
        return query

    def _get_type_query(self):
        query = """
        SELECT
            cc.type as type,
            cc.easy_employe_cc_settlement_id as id, 
            sum(cc.amount_salary) as salary,
            sum(cc.amount_advancement) as advancement, 
            sum(cc.amount_payment) as payment
        FROM easy_employee_cc as cc
            inner join hr_employee hr on cc.employee_id = hr.id
        """
        if self.filter_settlement_ids:
            query += """ and cc.easy_employe_cc_settlement_id in %s """
        query += """
        WHERE date between %s and %s
         """
        if self.filter_account_ids:
            query += """ and cc.employee_id in %s """
        if self.filter_company_ids:
            query += """ and hr.company_id in %s """
        if self.filter_settlement_type:
            query += """ and cc.settlement_type like %s """
        if self.description and len(self.description) > 0:
            query += \
                self.make_domain('cc.description', self.description)
        query += """
        GROUP BY cc.type,cc.easy_employe_cc_settlement_id
        """
        return query

    def _get_move_query(self):
        query = """
        SELECT
            cc.date,
            cc.employee_id,
            cc.type,
            cc.description, 
            cc.settlement_type,
            cc.easy_employe_cc_settlement_id as settlement_id,
            cc.amount_salary as salary,
            cc.amount_advancement as advancement, 
            cc.amount_payment  as payment
        FROM easy_employee_cc as cc
            inner join hr_employee hr on cc.employee_id = hr.id
            
        """
        if self.filter_settlement_ids:
            query += """ and cc.easy_employe_cc_settlement_id in %s """
        query += """
        WHERE date between %s and %s
         """
        if self.filter_account_ids:
            query += """ and cc.employee_id in %s """
        if self.filter_company_ids:
            query += """ and hr.company_id in %s """
        if self.filter_settlement_type:
            query += """ and cc.settlement_type like %s """
        if self.description and len(self.description) > 0:
            query += \
                self.make_domain('cc.description', self.description)
        query += """
        ORDER BY 
            cc.employee_id,
            cc.type,
            cc.date
            
        """
        return query

    def _inject_employee_values(self):

        employee_query = self._get_employee_query()

        query_inject_account_params = ()
        query_inject_account = """ WITH """
        query_inject_account += """
        Employees AS ( """ + employee_query + """ )"""

        query_inject_account += """
            INSERT INTO
                report_employee_employee
                (
                report_id,
                create_uid,
                create_date,
                employee_id,
                salary,
                advancement,
                payment,
                type_id
                )
            SELECT
                %s AS report_id,
                %s AS create_uid,
                NOW() AS create_date,
                e.employee_id,
                e.salary,
                e.advancement,
                e.payment,
                t.id
            FROM
                Employees e 
                inner join report_employee_type t
                on e.type = t.type_id and t.report_id = %s
                """
        
        query_inject_account_params += (
            self.date_from,
            self.date_to)
        if self.filter_settlement_ids and self.filter_settlement_ids.ids:
            query_inject_account_params += (
                tuple(self.filter_settlement_ids.ids),
            )
        if self.filter_account_ids and self.filter_account_ids.ids:
            query_inject_account_params += (
                tuple(self.filter_account_ids.ids),
            )
        if self.filter_company_ids and self.filter_company_ids.ids:
            query_inject_account_params += (
                tuple(self.filter_company_ids.ids),
            )
        if self.filter_settlement_type:
            query_inject_account_params += (self.filter_settlement_type,)
        if self.description and len(self.description) > 0:
            query_inject_account_params += \
                tuple(self.insert_domain('cc.description', self.description))
        query_inject_account_params += (
            self.id,
            self.env.uid,
            self.id,
        )
        _logger.debug(query_inject_account)
        _logger.debug(query_inject_account_params)
        _logger.debug(query_inject_account % query_inject_account_params)
        self.env.cr.execute(query_inject_account, query_inject_account_params)

    def _inject_type_values(self):

        type_query = self._get_type_query()

        query_inject_account_params = ()
        query_inject_account = """ WITH """
        query_inject_account += """
        TYPES AS ( """ + type_query + """ )"""

        query_inject_account += """
            INSERT INTO
                report_employee_type
                (
                report_id,
                create_uid,
                create_date,
                type,
                type_id,
                salary,
                advancement,
                payment
                )
            SELECT
                %s AS report_id,
                %s AS create_uid,
                NOW() AS create_date,
                t.type,
                t.id,
                t.salary,
                t.advancement,
                t.payment
            FROM
                Types t
                
                """
        if self.filter_settlement_ids and self.filter_settlement_ids.ids:
            query_inject_account_params += (
                tuple(self.filter_settlement_ids.ids),
            )
        query_inject_account_params += (
            self.date_from,
            self.date_to)
        if self.filter_account_ids and self.filter_account_ids.ids:
            query_inject_account_params += (
                tuple(self.filter_account_ids.ids),
            )
        if self.filter_company_ids and self.filter_company_ids.ids:
            query_inject_account_params += (
                tuple(self.filter_company_ids.ids),
            )
        if self.filter_settlement_type:
            query_inject_account_params += (self.filter_settlement_type,)
        if self.description and len(self.description) > 0:
            query_inject_account_params += \
                tuple(self.insert_domain('cc.description', self.description))

        query_inject_account_params += (
            self.id,
            self.env.uid,
        )
        _logger.debug(query_inject_account)
        _logger.debug(query_inject_account_params)
        _logger.debug(query_inject_account % query_inject_account_params)
        self.env.cr.execute(query_inject_account, query_inject_account_params)

    def _inject_move_values(self):

        move_query = self._get_move_query()

        query_inject_account_params = ()
        query_inject_account = """ WITH """
        query_inject_account += """
        MOVES AS ( """ + move_query + """ )"""

        query_inject_account += """
            INSERT INTO
                report_employee_move
                (
                report_id,
                create_uid,
                create_date,
                date,
                description,
                settlement_type,
                employee_id,
                salary,
                advancement,
                payment,
                settlement_id
                )
            SELECT
                %s AS report_id,
                %s AS create_uid,
                NOW() AS create_date,
                m.date,
                m.description,
                m.settlement_type,
                e.id,
                m.salary,
                m.advancement,
                m.payment,
                m.settlement_id
            FROM
                Moves m
                inner join report_employee_employee e
                on m.employee_id = e.employee_id and e.report_id = %s
                inner join report_employee_type t
                on m.settlement_id = t.type_id and t.report_id = %s
                and t.id=e.type_id 
                """
        if self.filter_settlement_ids and self.filter_settlement_ids.ids:
            query_inject_account_params += (
                tuple(self.filter_settlement_ids.ids),
            )
        query_inject_account_params += (
            self.date_from,
            self.date_to)
        if self.filter_account_ids and self.filter_account_ids.ids:
            query_inject_account_params += (
                tuple(self.filter_account_ids.ids),
            )
        if self.filter_company_ids and self.filter_company_ids.ids:
            query_inject_account_params += (
                tuple(self.filter_company_ids.ids),
            )
        if self.filter_settlement_type:
            query_inject_account_params += (self.filter_settlement_type,)
        if self.description and len(self.description) > 0:
            query_inject_account_params += \
                tuple(self.insert_domain('cc.description', self.description))

        query_inject_account_params += (
            self.id,
            self.env.uid,
            self.id,
            self.id,
        )
        _logger.debug(query_inject_account)
        _logger.debug(query_inject_account_params)
        _logger.debug(query_inject_account % query_inject_account_params)
        self.env.cr.execute(query_inject_account, query_inject_account_params)

    @api.multi
    def compute_data_for_report(self):
        self.ensure_one()
        
        self._inject_type_values()
        if self.detail:
            self._inject_employee_values()
            self._inject_move_values()
