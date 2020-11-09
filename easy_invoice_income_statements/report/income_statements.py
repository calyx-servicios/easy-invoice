# © 2018 Forest and Biomass Romania SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from ast import literal_eval
from odoo.exceptions import UserError
from datetime import timedelta
import time
import datetime
from collections import OrderedDict


class IncomeStatementsReport(models.TransientModel):
    """ Here, we just define class fields.
    For methods, go more bottom at this file.

    The class hierarchy is :
    * IncomeStatements
    *** IncomeStatementsAccount

    """

    _name = "report_income_statements"
    _inherit = "account_financial_report_abstract"

    # Filters fields, used for data computation
    date_from = fields.Date()
    date_to = fields.Date()
    company_id = fields.Many2one("res.company", index=True)
    filter_company_ids = fields.Many2many(comodel_name="res.company")
    filter_account_ids = fields.Many2many(
        comodel_name="account.analytic.account"
    )

    filter_category_ids = fields.Many2many(
        comodel_name="product.category"
    )
    filter_product_ids = fields.Many2many(
        comodel_name="product.product"
    )

    # Data fields, used to browse report data
    account_ids = fields.One2many(
        comodel_name="report_income_statements_account",
        inverse_name="report_id",
    )

    category_ids = fields.One2many(
        comodel_name="report_income_statements_category",
        inverse_name="report_id",
    )
    show_lines = fields.Boolean(default=True)

    # split by month
    by_month = fields.Boolean("Split by Month")

    parent_id = fields.Many2one(
        comodel_name="report_income_statements",
        ondelete="cascade",
        index=True,
    )
    # Data fields, used to browse report data
    child_ids = fields.One2many(
        comodel_name="report_income_statements",
        inverse_name="parent_id",
    )

    def formatDate(self, dtDateTime, strFormat="%Y-%m-%d"):
        # format a datetime object as YYYY-MM-DD string and return
        return dtDateTime.strftime(strFormat)

    def mkDateTime(self, dateString, strFormat="%Y-%m-%d"):
        # Expects "YYYY-MM-DD" string
        # returns a datetime object
        eSeconds = time.mktime(time.strptime(dateString, strFormat))
        return datetime.datetime.fromtimestamp(eSeconds)

    def mkFirstOfMonth(self, dtDateTime):
        # what is the first day of the current month
        # format the year and month + 01
        # for the current datetime
        # then form it back
        # into a datetime object
        return self.mkDateTime(self.formatDate(dtDateTime, "%Y-%m-01"))

    def mkLastOfMonth(self, dtDateTime):
        if int(dtDateTime.strftime("%m")) == 12:
            dYear = str(int(dtDateTime.strftime("%Y")) + 1)
        else:
            dYear = dtDateTime.strftime("%Y")  # get the year
        dMonth = str(
            int(dtDateTime.strftime("%m")) % 12 + 1
        )  # get next month, watch rollover
        dDay = "1"  # first day of next month
        nextMonth = self.mkDateTime(
            "%s-%s-%s" % (dYear, dMonth, dDay)
        )  # make a datetime obj for 1st of next month
        delta = datetime.timedelta(
            seconds=1
        )  # create a delta of 1 second
        return nextMonth - delta

    def _prepare_report_income_statements_child(self, start, end):
        self.ensure_one()
        return {
            "date_from": start,
            "date_to": end,
            "company_id": self.company_id.id,
            "filter_account_ids": [(6, 0, self.filter_account_ids.ids)],
            "filter_category_ids": [
                (6, 0, self.filter_category_ids.ids)
            ],
            "filter_product_ids": [(6, 0, self.filter_product_ids.ids)],
            "filter_company_ids": [(6, 0, self.filter_company_ids.ids)],
            "show_lines": self.show_lines,
            "parent_id": self.id,
        }

    def get_childs(self):
        start = datetime.datetime.strptime(self.date_from, "%Y-%m-%d")
        end = datetime.datetime.strptime(self.date_to, "%Y-%m-%d")
        months = OrderedDict(
            ((start + timedelta(_)).strftime(r"%m-%y"), None)
            for _ in range((end - start).days)
        ).keys()
        for month in months:
            _month = datetime.datetime.strptime(month, "%m-%y")
            first = self.mkFirstOfMonth(_month)
            last = self.mkLastOfMonth(_month)
            if first < start:
                first = start
            if last > end:
                last = end
            model = self.env["report_income_statements"]
            report_child = model.create(
                self._prepare_report_income_statements_child(
                    first, last
                )
            )
            report_child.compute_data_for_report()


class IncomeStatementsReportCategory(models.TransientModel):
    _name = "report_income_statements_category"
    _inherit = "account_financial_report_abstract"
    _order = "report_id, sequence"

    report_id = fields.Many2one(
        comodel_name="report_income_statements",
        ondelete="cascade",
        index=True,
    )

    category_id = fields.Many2one("product.category", index=True)

    root_category_id = fields.Many2one(
        comodel_name="report_income_statements_category",
        ondelete="cascade",
        index=True,
    )
    category_ids = fields.One2many(
        comodel_name="report_income_statements_category",
        inverse_name="root_category_id",
    )
    # Data fields, used to browse report data
    account_ids = fields.One2many(
        comodel_name="report_income_statements_account",
        inverse_name="root_category_id",
    )
    name = fields.Char(string="Category")
    balance = fields.Float(digits=(16, 2))
    sequence = fields.Integer(index=True, default=0)
    hide_category = fields.Boolean(default=True)
    percentage = fields.Boolean(default=False)

    def calculate_total(self):
        # calculates balance of self category and sums the
        # balances of his category childs
        balance = 0.0
        for account in self.account_ids:
            # sums the accounts balance associated with this category
            balance += account.balance

        for _category in self.category_ids:
            balance += _category.calculate_total()
        self.balance = balance

        return balance

    def print(self):
        if not self.root_category_id:
            for category in self.category_ids:
                category.print()

    def hide(self, hide=False):
        self.hide_category = hide
        for category in self.category_ids:
            category.hide(hide)


class IncomeStatementsReportAccount(models.TransientModel):
    _name = "report_income_statements_account"
    _inherit = "account_financial_report_abstract"
    _order = "report_id, root_category_id, product_id"

    report_id = fields.Many2one(
        comodel_name="report_income_statements",
        ondelete="cascade",
        index=True,
    )

    # Data fields, used to keep link with real object
    account_id = fields.Many2one("account.analytic.account", index=True)

    code = fields.Char()
    name = fields.Char()

    currency_id = fields.Many2one("res.currency")
    balance = fields.Float(digits=(16, 2))
    balance_foreign_currency = fields.Float(digits=(16, 2))

    product_id = fields.Many2one("product.product", index=True)

    root_category_id = fields.Many2one(
        comodel_name="report_income_statements_category",
        ondelete="cascade",
        index=True,
    )

    category_id = fields.Many2one("product.category", index=True)


class IncomeStatementsReportCompute(models.TransientModel):
    """ Here, we just define methods.
    For class fields, go more top at this file.
    """

    _inherit = "report_income_statements"

    @api.multi
    def print_report(self, report_type):
        self.ensure_one()
        if report_type == "xlsx":
            report_name = "easy_invoice_income_statements.income_statements_report_xlsx"
        else:
            report_name = "easy_invoice_income_statements.income_statements_report_qweb"
        res = (
            self.env["ir.actions.report"]
            .search(
                [
                    ("report_name", "=", report_name),
                    ("report_type", "=", report_type),
                ],
                limit=1,
            )
            .report_action(self)
        )
        return res

    def _get_html(self):
        result = {}
        rcontext = {}
        context = dict(self.env.context)
        report = self.browse(context.get("active_id"))
        if report:
            rcontext["o"] = report
            result["html"] = self.env.ref(
                "easy_invoice_income_statements.report_income_statements"
            ).render(rcontext)
        return result

    @api.model
    def get_html(self, given_context=None):
        return self._get_html()

    @api.multi
    def compute_data_for_report(self):
        self.ensure_one()

        # Compute Income Statements Report Data.
        # The data of Income Statements Report
        # are based on Account Analytic Lines data.

        # First we verify that the configuration is correct.
        self._verify_configuration()

        # Compute report data

        # report lines creation based on filters passed by the wizzard
        self._inject_account_values()

        # build dashboard with configured categories
        self._build_dashboard()

        # updates account with category groups ids.
        # This is necesary to allow qweb navigation
        self._inject_account_category_update()

        # calculates balance for every category recursevely
        self._calculate_total_dashboard()

        # calculates profits for dashboard
        self._set_dashboard_category_key_balance()

        self._hide()
        # Refresh cache because all data are computed with SQL requests
        self.invalidate_cache()

        if self.by_month and not self.parent_id:
            self.get_childs()

    def _get_category_keys(self):
        ICPSudo = self.env["ir.config_parameter"].sudo()
        category_names = [
            "category_sales",
            "category_commodities",
            "category_gross_profit",
            "category_gross_profit_percentage",
            "category_expenses",
            "category_net_profit",
            "category_net_profit_percentage",
        ]
        categories = []
        for name in category_names:

            category_id = literal_eval(
                ICPSudo.get_param(
                    "easy_invoice_income_statements." + name,
                    default="False",
                )
            )
            category = self.env["product.category"].browse(category_id)
            sequence = category.sequence
            categories.append(
                {
                    "name": name,
                    "id": category_id,
                    "sequence": sequence,
                    "balance": 0.0,
                }
            )

        categories = sorted(categories, key=lambda c: c["sequence"])
        return categories

    def _verify_configuration(self):

        ICPSudo = self.env["ir.config_parameter"].sudo()
        categories = self._get_category_keys()
        for key in categories:
            if key["name"] not in ("category_expenses"):
                if not key["id"]:
                    raise UserError(
                        _(
                            "You must configure all categories for this report. \
                                 Please, verify your \
                                      Income Statement Report Configuration"
                        )
                    )
        category_expense_ids = literal_eval(
            ICPSudo.get_param(
                "easy_invoice_income_statements.category_expense_ids",
                default="False",
            )
        )
        if not category_expense_ids or len(category_expense_ids) <= 0:
            raise UserError(
                _(
                    "You must configure at least one expense category for this \
                        report. Please, verify your \
                             Income Statement Report Configuration"
                )
            )

    def _set_dashboard_category_key_balance(self):
        # Here we apply the Business logic to calculate
        # profit different variables.
        ICPSudo = self.env["ir.config_parameter"].sudo()
        categories = self._get_category_keys()
        dashboard = {}
        for key in categories:
            dashboard[key["name"]] = key
        for key in dashboard:
            category = self.env[
                "report_income_statements_category"
            ].search(
                [
                    ("category_id", "=", dashboard[key]["id"]),
                    ("report_id", "=", self.id),
                ]
            )
            dashboard[key]["balance"] = category.balance

        dashboard["category_gross_profit"]["balance"] = (
            dashboard["category_sales"]["balance"]
            + dashboard["category_commodities"]["balance"]
        )
        category = self.env["report_income_statements_category"].search(
            [
                (
                    "category_id",
                    "=",
                    dashboard["category_gross_profit"]["id"],
                ),
                ("report_id", "=", self.id),
            ]
        )
        if category:
            category.balance = dashboard["category_gross_profit"][
                "balance"
            ]

        # calculates and store category_gross_profit_percentage value
        if dashboard["category_sales"]["balance"] != 0:
            dashboard["category_gross_profit_percentage"]["balance"] = (
                dashboard["category_gross_profit"]["balance"]
                / dashboard["category_sales"]["balance"]
            )
            category = self.env[
                "report_income_statements_category"
            ].search(
                [
                    (
                        "category_id",
                        "=",
                        dashboard["category_gross_profit_percentage"][
                            "id"
                        ],
                    ),
                    ("report_id", "=", self.id),
                ]
            )
            if category:
                category.balance = (
                    dashboard["category_gross_profit_percentage"][
                        "balance"
                    ]
                    * 100
                )
                category.percentage = True

        expenses = 0.0
        category_expense_ids = literal_eval(
            ICPSudo.get_param(
                "easy_invoice_income_statements.category_expense_ids",
                default="False",
            )
        )
        for category in self.env["product.category"].browse(
            category_expense_ids
        ):
            for _category in self.env[
                "report_income_statements_category"
            ].search(
                [
                    ("category_id", "=", category.id),
                    ("report_id", "=", self.id),
                ]
            ):
                expenses += _category.balance
        dashboard["category_expenses"]["balance"] = expenses
        dashboard["category_net_profit"]["balance"] = (
            dashboard["category_gross_profit"]["balance"]
            + dashboard["category_expenses"]["balance"]
        )
        category = self.env["report_income_statements_category"].search(
            [
                (
                    "category_id",
                    "=",
                    dashboard["category_net_profit"]["id"],
                ),
                ("report_id", "=", self.id),
            ]
        )
        if category:
            category.balance = dashboard["category_net_profit"][
                "balance"
            ]

        # calculates and store category_netprofit_percentage value
        if dashboard["category_sales"]["balance"] != 0:
            dashboard["category_net_profit_percentage"]["balance"] = (
                dashboard["category_net_profit"]["balance"]
                / dashboard["category_sales"]["balance"]
            )
            category = self.env[
                "report_income_statements_category"
            ].search(
                [
                    (
                        "category_id",
                        "=",
                        dashboard["category_net_profit_percentage"][
                            "id"
                        ],
                    ),
                    ("report_id", "=", self.id),
                ]
            )
            if category:
                category.balance = (
                    dashboard["category_net_profit_percentage"][
                        "balance"
                    ]
                    * 100
                )
                category.percentage = True

    def _calculate_total_dashboard(self):

        for category in self.category_ids:
            if not category.root_category_id:
                category.calculate_total()

    def _hide(self):
        if self.filter_product_ids or self.filter_category_ids:
            # hide everything
            for category in self.category_ids:
                category.hide(True)

            if self.filter_product_ids:
                # set visible only categories wich are included inside
                # filter_products_ids and their childs
                category_ids = []
                for product in self.env["product.product"].browse(
                    self.filter_product_ids.ids
                ):
                    cat_id = product.product_tmpl_id.categ_id.id
                    if self.filter_category_ids:
                        if cat_id in self.filter_category_ids.ids:
                            category_ids.append(cat_id)
                    else:
                        category_ids.append(cat_id)
            else:
                category_ids = self.filter_category_ids.ids
            categories_ids = (
                self.env["report_income_statements_category"]
                .search(
                    [
                        ("category_id", "in", category_ids),
                        ("report_id", "=", self.id),
                    ]
                )
                .ids
            )
            for category in self.env[
                "report_income_statements_category"
            ].browse(categories_ids):
                category.hide(False)

    def _build_dashboard(self):
        ICPSudo = self.env["ir.config_parameter"].sudo()
        categories = self._get_category_keys()
        category_obj = self.env["product.category"]

        sequence = 1
        expense_category_root = None
        for key in categories:

            if key["name"] not in (
                "category_net_profit",
                "category_net_profit_percentage",
                "category_expenses",
            ):

                category = category_obj.browse(key["id"])
                sequence = self._inject_category_values(
                    category, sequence
                )
                # This could be required after Nahue, maybe now they want
                # to resume expenses to only one root expense category
                # If that is the case, you must uncomment this field,
                # and insert the expense categories hidden.

                # if key['name'] in ('category_expenses'):
                #     expense_category_root=self.env['report_income_statements_category'].search([('category_id','=',category.id),('report_id','=',self.id),('root_category_id','=',None)])

        category_expense_ids = literal_eval(
            ICPSudo.get_param(
                "easy_invoice_income_statements.category_expense_ids",
                default="False",
            )
        )
        category_expense_ids = category_obj.search(
            [("id", "in", category_expense_ids)], order="sequence"
        ).ids
        # category_expense_ids = set(category_expense_ids)
        for category in category_obj.browse(category_expense_ids):
            # expense_category_root is not set by default,
            # but I think that it will be soon. After Nahue
            sequence = self._inject_category_values(
                category,
                sequence,
                hide=False,
                root=expense_category_root,
            )
        for key in categories:
            if key["name"] in (
                "category_net_profit",
                "category_net_profit_percentage",
            ):
                category = category_obj.browse(key["id"])
                sequence = self._inject_category_values(
                    category, sequence
                )

    def _inject_category_values(
        self, _category, sequence, hide=False, root=None
    ):
        # check if was not created before due to users
        # category tree manipulations.
        created_category = self.env[
            "report_income_statements_category"
        ].search(
            [
                ("category_id", "=", _category.id),
                ("report_id", "=", self.id),
                ("root_category_id", "=", root and root.id),
            ]
        )
        if not created_category:
            sequence = self._inject_category_values_query(
                _category, sequence, hide, root
            )
            created_category = self.env[
                "report_income_statements_category"
            ].search(
                [
                    ("category_id", "=", _category.id),
                    ("report_id", "=", self.id),
                    ("root_category_id", "=", root and root.id),
                ]
            )
            for category in _category.child_id:
                sequence = self._inject_category_values(
                    category,
                    sequence,
                    not self.show_lines,
                    created_category,
                )
        return sequence

    def _inject_category_values_query(
        self, category, sequence, hide=False, root=None
    ):
        query_inject_params = ()
        query_inject = """
        INSERT INTO report_income_statements_category(
            report_id,
            create_uid,
            category_id,
            name,
            sequence,
            root_category_id,
            hide_category
        )
        SELECT
            %s as report_id,
            %s as create_uid,
            %s as category,
            %s as name,
            %s as sequence,
            %s as root,
            %s as hide

        """
        query_inject_params += (
            self.id,
            self._uid,
            category.id,
            category.name,
            sequence,
            root and root.id,
            hide,
        )
        self.env.cr.execute(query_inject, query_inject_params)
        sequence += 1
        return sequence

    def _inject_account_category_update(self):
        query_inject_params = ()
        query_inject = """
        UPDATE
            report_income_statements_account
        SET
            root_category_id = ag.id
        FROM
            report_income_statements_category as ag
        WHERE
            ag.category_id = report_income_statements_account.category_id
            AND ag.report_id = report_income_statements_account.report_id
            AND report_income_statements_account.report_id = %s

        """
        query_inject_params += (self.id,)
        self.env.cr.execute(query_inject, query_inject_params)

    def _inject_account_values(self):
        """Inject report values for report_income_statements_account"""

        amount_subquery = self._get_account_sub_subquery_sum_amounts(
            self.filter_company_ids
        )
        accounts_subquery = self._get_account_sub_subquery(
            self.filter_account_ids
        )
        query_inject_account_params = ()
        query_inject_account = """ WITH """
        query_inject_account += (
            """
        sum_amounts AS ( """
            + amount_subquery
            + """ ),
        accounts as ( """
            + accounts_subquery
            + """)"""
        )

        query_inject_account += """
            INSERT INTO
                report_income_statements_account
                (
                report_id,
                create_uid,
                create_date,
                account_id,
                code,
                name,
                product_id,
                category_id,
                balance,
                currency_id
                )
            SELECT
                %s AS report_id,
                %s AS create_uid,
                NOW() AS create_date,
                a.account_id AS account_id,
                a.code,
                a.name,
                s.product_id,
                s.category_id,
                COALESCE(s.amount, 0.0) AS balance,
                s.currency_id
            FROM
                accounts a
                INNER JOIN
                    sum_amounts s ON a.account_id = s.account_id


                """

        if self.filter_product_ids:
            query_inject_account += """ AND s.product_id IN %s """

        query_inject_account_params += (
            self.date_from,
            self.date_to,
        )
        if self.filter_company_ids:
            query_inject_account_params += (
                tuple(self.filter_company_ids.ids),
            )
        if self.filter_account_ids:
            query_inject_account_params += (
                tuple(self.filter_account_ids.ids),
            )
        query_inject_account_params += (
            self.id,
            self._uid,
        )

        if self.filter_product_ids:
            query_inject_account_params += (
                tuple(self.filter_product_ids.ids),
            )
        # INYECTA VALORES
        self.env.cr.execute(
            query_inject_account, query_inject_account_params
        )

    def _get_account_sub_subquery_sum_amounts(
        self, company_filtered=False
    ):
        """ Return subquery used to compute sum amounts on accounts """
        sub_subquery_sum_amounts = """
            SELECT
                a.id AS account_id,
                ml.product_id as product_id,
                ml.product_category_id as category_id,
                SUM(ml.amount) AS amount,
                c.id AS currency_id,
                CASE
                    WHEN c.id IS NOT NULL
                    THEN SUM(ml.amount_currency)
                    ELSE NULL
                END AS balance_currency
            FROM
                account_analytic_account a
            INNER JOIN
                account_analytic_line ml
                    ON a.id = ml.account_id
        """

        sub_subquery_sum_amounts += """
            AND ml.date >= %s
            AND ml.date <= %s
        """
        if company_filtered:
            sub_subquery_sum_amounts += """
                AND ml.company_id IN %s
            """

        sub_subquery_sum_amounts += """
        LEFT JOIN
            res_currency c ON ml.currency_id = c.id
        """
        sub_subquery_sum_amounts += """
        GROUP BY
            a.id, ml.product_id,
            ml.product_category_id,c.id
        ORDER BY
            a.name,
            ml.product_category_id,
            ml.product_id


        """
        return sub_subquery_sum_amounts

    def _get_account_sub_subquery(self, account_filtered=False):
        """ Return subquery used to get accounts """
        sub_subquery = """
            SELECT
                aa.id AS account_id,
                aa.code as code,
                aa.name as name
            FROM
                account_analytic_account aa

                """
        if account_filtered:
            sub_subquery += """
            where aa.id IN %s """
        sub_subquery += """
        Order BY
            aa.code
        """
        return sub_subquery
