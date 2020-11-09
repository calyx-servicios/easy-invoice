# © 2016 Julien Coux (Camptocamp)
# © 2018 Forest and Biomass Romania SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.tools import float_is_zero
from ast import literal_eval
from odoo.exceptions import AccessError, UserError
import logging

_logger = logging.getLogger(__name__)


class CustomerAccountReport(models.TransientModel):
    """ Here, we just define class fields.
    For methods, go more bottom at this file.

    The class hierarchy is :
    * CustomerAccountReport

    """

    _name = 'report_customer_account'
    _inherit = 'account_financial_report_abstract'

    # Filters fields, used for data computation
    date_from = fields.Date()
    date_to = fields.Date()
    company_id = fields.Many2one(
        'res.company',
        index=True
    )
    filter_company_ids = fields.Many2many(comodel_name='res.company')
    filter_account_ids = fields.Many2many(comodel_name='res.partner')

    # Data fields, used to browse report data
    partner_ids = fields.One2many(
        comodel_name='report_customer_account_partner',
        inverse_name='report_id'
    )
    non_zero = fields.Boolean(default=False)


class CustomerAccountReportPartner(models.TransientModel):
    _name = 'report_customer_account_partner'
    _inherit = 'account_financial_report_abstract'
    _order = 'report_id'

    report_id = fields.Many2one(
        comodel_name='report_customer_account',
        ondelete='cascade',
        index=True
    )

    partner_id = fields.Many2one(
        'res.partner',
        index=True
    )

    # Data fields, used to browse report data
    move_ids = fields.One2many(
        comodel_name='report_customer_account_move',
        inverse_name='report_partner_id'
    )

    initial = fields.Float(digits=(16, 2))
    final = fields.Float(digits=(16, 2))
    visible = fields.Boolean(default=True)


class CustomerAccountReportMove(models.TransientModel):
    _name = 'report_customer_account_move'
    _inherit = 'account_financial_report_abstract'

    report_id = fields.Many2one(
        comodel_name='report_customer_account',
        ondelete='cascade',
        index=True
    )

    partner_id = fields.Many2one(
        'res.partner',
        index=True
    )

    report_partner_id = fields.Many2one(
        comodel_name='report_customer_account_partner',
        ondelete='cascade',
        index=True
    )

    description = fields.Char()
    detail = fields.Char()

    initial = fields.Float(digits=(16, 2))
    debit = fields.Float(digits=(16, 2))
    credit = fields.Float(digits=(16, 2))
    accumulate = fields.Float(digits=(16, 2))

    computed = fields.Float(string='Accumulate')

    expiry_date = fields.Char()
    move_date = fields.Date()

    easy_invoice_id = fields.Many2one(
        'easy.invoice',
        index=True
    )

    type_refund = fields.Selection([('returns', 'Devoluciones'),
                                    ('withdrawal', 'Retiro'),
                                    ('corrections', 'Correciones'),
                                    ('combo', 'Combo (Marketing)'),
                                    ('various', 'Varios'),
                                    ], string="Type Refund", translate=True, related='easy_invoice_id.type_refund')


class CustomerAccountReportCompute(models.TransientModel):
    """ Here, we just define methods.
    For class fields, go more top at this file.
    """

    _inherit = 'report_customer_account'

    def _get_partners_query(self):
        query = """

        select partner_id as partner_id, report_id, id as report_partner_id, initial
        from report_customer_account_partner
        """
        if self.filter_account_ids:
            query += """ where partner_id in %s """
        return query

    def _get_query(self, date_from, date_to=None):
        query = """
            select partner_id as partner_id, move_date as move_date,
            Name as description, invoice_id as invoice_id, debit as debit, credit as credit, 
            (sum (total) OVER (PARTITION by partner_id order by move_date asc, payment_id))-total AS initial, 
            sum (total) OVER (PARTITION by partner_id order by move_date asc, payment_id) AS accumulate,
            expiry_date::varchar as expiry_date
            from (
            (select  epcc.partner_id as partner_id,
                Null as invoice_id,
                epcc.payment_id as payment_id,
                epcc.date::date as move_date,
                p.sequence_number as Name,
                '' as type,
                0  as debit,  		
                epcc.amount_anticipe as credit, 
                -epcc.amount_anticipe total,
                Null::date as expiry_date
            from easy_partner_cc as epcc join easy_payment as p on (epcc.payment_id = p.id)
            where epcc.amount_anticipe > 0.0 and epcc.state like 'open' ) 
            union all
            (select i.partner_id as partner_id, p.invoice_id invoice_id, 
            p.id as payment_id,  p.date_pay as move_date, i.name as Name, i.type as type, 
            p.amount_total as debit, 0  as credit, p.amount_total total, i.date_expiration as expiry_date
            from easy_payment as p left join easy_invoice as i on p.invoice_id = i.id
            where 
            i.state in ('open','paid') and i.type like 'out_invoice' and p.name like 'Residual' and p.amount_out = 0.0 
            and p.type like 'pay_out'
            order by p.date_pay)
            union all
            (select i.partner_id as partner_id, p.invoice_id invoice_id, 
            p.id as payment_id,  p.date_pay as move_date, i.name as Name, i.type as type, 
            0 as debit, p.amount_total  as credit, -p.amount_total total, i.date_expiration expiry_date
            from easy_payment as p left join easy_invoice as i on p.invoice_id = i.id
            where 
            i.state in ('open','paid') and i.type like 'out_refund' and p.name like 'Residual' and p.amount_in = 0.0 
            and p.type like 'pay_in'
            order by p.date_pay)
            union all
            (select i.partner_id as partner_id, p.invoice_id invoice_id, p.id as payment_id, p.date_pay as move_date, 
            p.sequence_number as Name, p.type as type,
            0 as debit, p.amount_total as credit, -p.amount_total total, NULL as expiry_date
            from easy_payment as p left join easy_invoice as i on p.invoice_id = i.id 
            where 
            p.amount_in is null and p.type like 'pay_out'
            order by p.date_pay)
            ) as foo
            where """
        if self.filter_account_ids:
            query += """ partner_id in %s and """
        if date_from and date_to:
            query += """  move_date between %s and %s """
        else:
            query += """ move_date < %s """
        query += """   order by partner_id, expiry_date
            """
        return query

    def _inject_account_values(self):

        accounts_query = self._get_query(self.date_from, self.date_to)
        partners_query = self._get_partners_query()
        query_inject_account_params = ()
        query_inject_account = """ WITH """
        query_inject_account += """
        Moves AS ( """ + accounts_query + """ ),"""
        query_inject_account += """
        Partners AS ( """ + partners_query + """ ) """

        query_inject_account += """
            INSERT INTO
                report_customer_account_move
                (
                report_id,
                create_uid,
                create_date,
                partner_id, 
                move_date,
                description,
                easy_invoice_id, 
                debit, 
                credit, 
                initial, 
                accumulate,
                expiry_date,
                report_partner_id
                )
            SELECT
                %s AS report_id,
                %s AS create_uid,
                NOW() AS create_date,
                a.partner_id,
                a.move_date,
                a.description,
                a.invoice_id,
                a.debit,
                a.credit,
                p.initial,
                a.accumulate,
                a.expiry_date,
                p.report_partner_id
            FROM
                Moves as a left join Partners  as p
                on a.partner_id = p.partner_id and p.report_id = %s 

                """
        if self.filter_account_ids:
            query_inject_account_params += (tuple(
                self.filter_account_ids._ids),)
        query_inject_account_params += (
            self.date_from,
            self.date_to)
        if self.filter_account_ids:
            query_inject_account_params += (tuple(
                self.filter_account_ids._ids),)
        query_inject_account_params += (
            self.id,
            self.env.uid,
            self.id
        )
        _logger.debug(query_inject_account)
        _logger.debug(query_inject_account_params)
        _logger.debug(query_inject_account % query_inject_account_params)
        self.env.cr.execute(query_inject_account, query_inject_account_params)

    def _inject_partner_values(self):
        initial_query = self._get_query(self.date_from)

        query_inject_account_params = ()
        query_inject_account = """ """
        query_inject_account += """ WITH
        Initial AS ( """ + initial_query + """ ) """

        query_inject_account += """
            INSERT INTO
                report_customer_account_partner
                (
                report_id,
                create_uid,
                create_date,
                partner_id,
                initial,
                visible
                )
            SELECT
                %s AS report_id,
                %s AS create_uid,
                NOW() AS create_date,
                a.id,
                sum(i.debit-i.credit) as initial,
                true
            FROM
                res_partner as a 
                left outer join Initial as i
                on a.id=i.partner_id """
        if self.filter_account_ids:
            query_inject_account += """ WHERE a.id in %s """
        query_inject_account += """    
            GROUP BY a.id
                """
        if self.filter_account_ids:
            query_inject_account_params += (tuple(
                self.filter_account_ids._ids),)
        query_inject_account_params += (
            self.date_from,
            self.id,
            self.env.uid
        )
        if self.filter_account_ids:
            query_inject_account_params += (tuple(
                self.filter_account_ids._ids),)
        _logger.debug(query_inject_account)
        _logger.debug(query_inject_account_params)
        _logger.debug(query_inject_account % query_inject_account_params)
        self.env.cr.execute(query_inject_account, query_inject_account_params)

    @api.multi
    def fix_accumulate(self):
        for partner in self.partner_ids:
            initial = partner.initial
            for account in partner.move_ids:

                account.computed = initial+account.debit-account.credit
                initial += account.debit-account.credit
            partner.final = initial
            if self.non_zero:
                if partner.final == 0.0:
                    partner.visible = False

    @api.multi
    def compute_data_for_report(self):
        self.ensure_one()

        self._inject_partner_values()
        self._inject_account_values()
        self.fix_accumulate()
