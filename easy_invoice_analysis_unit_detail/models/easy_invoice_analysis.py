from odoo import fields, models, tools, api

class AnalysisReportLine(models.Model):
    """ Easy Analysis Report"""

    _inherit = 'easy_invoice_analysis_report'

    unit_detail = fields.Float('Unit Detail', (16,2))

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
    my_query.type_refund,
    my_query.description,
    my_query.date_due,
    my_query.unit_detail,
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
            l.type_refund AS type_refund,
            l.description AS description,
            l.date_due AS date_due,
            l.unit_detail AS unit_detail,
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
                    e.type_refund,
                    e.note AS description,
                    e.date_expiration AS date_due,
                    l_1.unit_detail,
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
                    'type_refund'::text AS type_refund, 
                    l_1.name AS description,
                    i.date_due,
                    l_1.unit_detail,
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
    my_query.type_refund,
    my_query.description,
    my_query.date_due,
    my_query.unit_detail,
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

