from odoo import fields, models, tools, api
import logging

_logger = logging.getLogger(__name__)


class AnalysisReportLine(models.Model):
    """ Easy Analysis Report"""

    _name = 'easy_invoice_analysis_report'
    _auto = False
    _description = "Easy Analysis Report"
    _rec_name = 'date'

    date = fields.Date(string='Date', readonly=True)

    user_id = fields.Many2one(
        'res.users',
        string='User',
        readonly=True)


    partner_categ_id = fields.Many2many(
        comodel_name='res.partner.category',
        string='Partner Category',
        relation='easy_analysis_report_partner_categ',
        related='partner_id.category_id'
    )



    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        readonly=True)
    categ_id = fields.Many2one(
        'product.category',
        string='Category',
        readonly=True)

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        readonly=True)
    product_id = fields.Many2one(
        'product.product', string='Product', readonly=True)
    uom_id = fields.Many2one('product.uom', 'Uom')
    product_type = fields.Selection(
        related='product_id.type',
        string='Product Type',
        readonly=True)
    origin = fields.Selection([
        ('easy', 'Easy Invoice'),
        ('invoice', 'Account Invoice'),
    ], string='Origin', readonly=True)
    type = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('in_invoice', 'Supplier Bill'),
        ('out_refund', 'Customer Credit Note'),
        ('in_refund', 'Supplier Credit Note'),
    ], string='Type Operation', readonly=True)
    journal_id = fields.Many2one(
        'account.journal', string='Journal', readonly=True)
    easy_id = fields.Many2one(
        'easy.envoice',
        string='Easy',
        readonly=True)

    name = fields.Char('Reference', readonly=True)
    description = fields.Char('Description')
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice',
        readonly=True)
    date_due = fields.Date(string='Date Due', readonly=True)
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
    ], string='State',  readonly=True)
    price_unit = fields.Float(string='Price Unit', digits=(
        16, 2), default=0, readonly=True)
    amount = fields.Float(string='Amount', digits=(
        16, 2), default=0, readonly=True)
    quantity = fields.Float(string='Quantity', digits=(
        16, 2), default=0, readonly=True)
    
    date_contable = fields.Date(string="Fecha Contable", readonly=True)

    def _select(self):
        query = """
        SELECT row_number() OVER ()::integer AS id,
    NULL::timestamp without time zone AS create_date,
    NULL::integer AS create_uid,
    NULL::timestamp without time zone AS write_date,
    NULL::integer AS write_uid,
    my_query.easy_id,
    my_query.invoice_id,
    my_query.state,
    my_query.date,
    my_query.partner_id,
    my_query.user_id,
    my_query.company_id,
    my_query.origin,
    my_query.product_id,
    my_query.quantity,
    my_query.amount,
    my_query.analytic_account_id,
    my_query.name,
    my_query.type,
    my_query.description,
    my_query.date_due,
    my_query.uom_id,
    my_query.journal_id,
    my_query.price_unit,
    my_query.categ_id,
    my_query.date_contable
   FROM ( SELECT 
            l.line_id as line_id,
            l.easy_id AS easy_id,
            l.invoice_id AS invoice_id,
            l.state AS state,
            l.date_invoice AS date,
            l.partner_id AS partner_id,
            l.user_id AS user_id,
            l.company_id AS company_id,
            l.origin AS origin,
            l.product_id AS product_id,
            (case when l.type like '"""+'%'+"""refund' then -l.quantity else  l.quantity end) AS quantity ,
            (case when l.type like '"""+'%'+"""refund' then -l.amount else  l.amount end) AS amount ,
            l.analytic_account_id AS analytic_account_id,
            l.name AS name,
            l.type AS type,
            l.description AS description,
            l.date_due AS date_due,
            l.uom_id AS uom_id,
            l.journal_id AS journal_id,
            l.price_unit AS price_unit,
            l.categ_id AS categ_id,
            l.date_contable AS date_contable
           FROM ( SELECT 
                    e.id AS easy_id,
                    NULL::integer AS invoice_id,
                    e.state,
                    e.date_invoice,
                    e.partner_id,
                    e.user_id,
                    e.company_id,
                    e.date_contable,
                    'easy'::text AS origin,
                    l_1.id as line_id,
                    l_1.product_id,
                    l_1.quantity,
                    l_1.price_subtotal AS amount,
                    l_1.analytic_account_id,
                    e.name,
                    e.type,
                    e.note AS description,
                    e.date_expiration AS date_due,
                    l_1.uom_id,
                    NULL::integer AS journal_id,
                    l_1.price_unit,
                    t.categ_id
                   FROM easy_invoice e
                     JOIN easy_invoice_line l_1 ON e.id = l_1.invoice_id
                     inner join product_product p
					 on l_1.product_id = p.id
					 inner join product_template t
					 on p.product_tmpl_id = t.id
                UNION ALL
                 SELECT NULL::integer AS easy_id,
                    i.id AS invoice_id,
                    i.state,
                    i.date_invoice,
                    i.partner_id,
                    i.user_id,
                    i.company_id,
                    i.date AS date_contable,
                    'invoice'::text AS origin,
                    l_1.id as line_id,
                    l_1.product_id,
                    l_1.quantity,
                    l_1.price_subtotal AS amount,
                    l_1.account_analytic_id,
                    m.display_name,
                    i.type,
                    l_1.name AS description,
                    i.date_due,
                    l_1.uom_id,
                    i.journal_id,
                    l_1.price_unit,
                    t.categ_id
                   FROM account_invoice i
                     JOIN account_invoice_line l_1 ON i.id = l_1.invoice_id
                     INNER JOIN account_move m on i.move_id = m.id
                     inner join product_product p
					 on l_1.product_id = p.id
					 inner join product_template t
					 on p.product_tmpl_id = t.id
                     ) l
                    
        
          ORDER BY l.date_invoice) my_query
          group by my_query.easy_id,
    my_query.invoice_id,
    my_query.state,
    my_query.date,
    my_query.partner_id,
    my_query.user_id,
    my_query.company_id,
    my_query.origin,
    my_query.product_id,
    my_query.line_id,
    my_query.quantity,
    my_query.amount,
    my_query.analytic_account_id,
    my_query.name,
    my_query.type,
    my_query.description,
    my_query.date_due,
    my_query.uom_id,
    my_query.journal_id,
    my_query.price_unit,
    my_query.categ_id,
    my_query.date_contable
        """
        return query

    def _init_easy_line_analysis_view(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE VIEW %s AS (
            %s
        )""" % (self._table, self._select()))

    @api.model_cr
    def init(self):
        self._init_easy_line_analysis_view()

