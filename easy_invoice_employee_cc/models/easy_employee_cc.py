# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class EasyEmployeeCC(models.Model):
    _inherit = ["mail.thread", "mail.activity.mixin", "portal.mixin"]
    _name = "easy.employee.cc"
    _order = "date desc,id desc"

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id

    # Fields
    description = fields.Char(string="Reference/Description",)
    date = fields.Date(string="Date",)
    date_contable = fields.Date(
        string="Contable Date",
        readonly=True,
        states={"draft": [("readonly", False)]},
        index=True,
        help="Keep empty to use the current date",
        copy=False,
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        readonly=True,
        default=_default_currency,
    )
    payment_id = fields.Many2one("easy.payment", string="Payment Related")
    recaudation_id = fields.Many2one(
        "easy.recaudation", string="Recaudation Related"
    )
    employee_id = fields.Many2one("hr.employee", string="Employee")

    amount_payment = fields.Monetary(string="Payment",)
    amount_residual_payment = fields.Monetary(string="Residual Payment",)
    amount_salary = fields.Monetary(string="Salary",)
    amount_advancement = fields.Monetary(string="Advancement",)
    user_id = fields.Many2one(
        "res.users",
        string="Responsible",
        readonly=True,
        default=lambda self: self.env.user,
        copy=False,
    )

    type = fields.Selection(
        [
            ("advancement", "Advancement"),
            ("bank", "Bank"),
            ("basic_salary", "Basic Salary"),
            ("liquidation_salary", "Liquidation Salary"),
        ],
        string="Type",
        default="advancement",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Done")],
        string="State",
        default="draft",
    )

    easy_employe_cc_settlement_id = fields.Many2one(
        "easy.employe.cc.settlement", string="Tipo"
    )
    settlement_type = fields.Selection(
        [
            ("haberes", "Haberes"),
            ("pagos_compesacion", "Pagos y Compensaciones"),
        ],
        string="Type",
        related="easy_employe_cc_settlement_id.ttype",
    )
    # end Fields

    @api.multi
    def create_movement(
        self,
        settlement,
        amount,
        employee_obj,
        description,
        recaudation_id,
        date,
        date_contable,
    ):
        line_created_cc = None
        ttype = settlement.profile
        deuda = settlement.symbol
        easy_movement = settlement.easy_movement
        vals = {}

        if deuda == "sum":
            vals = {
                "description": description,
                "employee_id": employee_obj.id,
                "amount_salary": amount,
                "amount_advancement": 0.0,
                "date": date,
                "date_contable": date_contable,
                "easy_employe_cc_settlement_id": settlement.id,
                "type": ttype,
            }
            if ttype == "liquidation_salary":
                vals.update(
                    {
                        "recaudation_id": recaudation_id.id,
                        "amount_salary": employee_obj.amount_residual * (-1.0),
                    }
                )
            if easy_movement == "yes":
                vals.update({"recaudation_id": recaudation_id.id})
                line_created_cc = self.env["easy.employee.cc"].create(vals)
                line_created_cc.create_recaudation_move()
            else:
                line_created_cc = self.env["easy.employee.cc"].create(vals)
            if ttype == "liquidation_salary":
                line_created_cc.amount_residual_payment = 0.0
            line_created_cc.state = "done"

        elif deuda == "subtraction":
            vals = {
                "description": description,
                "employee_id": employee_obj.id,
                "amount_salary": 0.0,
                "amount_advancement": amount,
                "date": date,
                "date_contable": date_contable,
                "easy_employe_cc_settlement_id": settlement.id,
                "type": ttype,
            }
            if easy_movement == "yes":
                vals.update({"recaudation_id": recaudation_id.id})
                line_created_cc = self.env["easy.employee.cc"].create(vals)
                line_created_cc.create_recaudation_move()
            else:
                line_created_cc = self.env["easy.employee.cc"].create(vals)
            line_created_cc.state = "done"
        return line_created_cc

    @api.multi
    def create_recaudation_move(self, amount2pay=0.0):
        for rec in self:
            recaudation_obj = rec.recaudation_id
            amount_total = 0.0  # rec.amount_salary + rec.amount_advancement
            amount_in = 0.0
            amount_out = 0.0
            sequence_number = ""
            payment_type = ""
            amount = 0.0
            # payment_type = 'retire'
            typee = rec.easy_employe_cc_settlement_id.symbol
            if typee == "sum":
                payment_type = "deposit"
                amount_in = rec.amount_advancement
                amount_out = rec.amount_salary
                amount_total = rec.amount_salary
                amount = rec.amount_salary
                sequence = recaudation_obj.configuration_sequence_id
                sequence_number = (
                    sequence.recaudation_deposit_sequence_id.next_by_id()
                )
            # if rec.type == 'advancement':
            if typee == "subtraction":
                if (
                    not recaudation_obj.boolean_permit_amount_negative
                    and recaudation_obj.amount_box - amount_total < 0.0
                ):
                    raise ValidationError(
                        _(
                            "You can not Retire without Funds. Make a "
                            "Transference or permit movement in negative"
                            " Amount"
                        )
                    )
                payment_type = "retire"
                amount_in = rec.amount_advancement
                amount_out = rec.amount_salary
                amount_total = rec.amount_advancement * (-1)
                amount = rec.amount_advancement
                seq = recaudation_obj.configuration_sequence_id
                sequence_number = (
                    seq.recaudation_retire_sequence_id.next_by_id()
                )

            vals = {
                "name": _(rec.description)
                + _(" a ")
                + _(rec.employee_id.name),
                "type": payment_type,
                "amount_total": amount_total,
                "amount_in": amount_in,
                "amount_out": amount_out,
                "recaudation_id": recaudation_obj.id,
                "date_pay": rec.date,
                "sequence_number": sequence_number,
            }
            line_created = self.env["easy.payment"].create(vals)
            recaudation_obj.subtract(amount)
            rec.payment_id = line_created.id
            return line_created

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.recaudation_id:
                raise ValidationError(
                    _(
                        "You cannot delete these type of movement!"
                        " because have easy payment relation"
                    )
                )
        return super(EasyEmployeeCC, self).unlink()

    @api.multi
    def print_salary_employee_cc(self):
        return self.env.ref(
            "easy_invoice_employee_cc.action_report_easyinvoice_employee"
        ).report_action(self)


class EasyEmployeeSettlement(models.Model):
    _name = "easy.employe.cc.settlement"

    sequence = fields.Integer(
        "Sequence", help="Used to order the 'All Operations' kanban view"
    )
    name = fields.Char(string="Name")
    profile = fields.Selection(
        [
            ("advancement", "Advancement"),
            ("bank", "Bank"),
            ("basic_salary", "Basic Salary"),
            ("liquidation_salary", "Liquidation Salary"),
        ],
        string="Profile",
    )
    easy_movement = fields.Selection(
        [("yes", "Yes"), ("no", "No")], string="Easy Movement", default="no"
    )
    symbol = fields.Selection(
        [("sum", "+"), ("subtraction", "-")], string="Symbol", default="sum"
    )
    ttype = fields.Selection(
        [
            ("haberes", "Haberes"),
            ("pagos_compesacion", "Pagos y Compensaciones"),
        ],
        string="Type",
        default="haberes",
    )

    state = fields.Selection(
        [("open", "Open"), ("archived", "Archived")],
        string="State",
        default="open",
    )

    @api.onchange("profile")
    def _onchange_type(self):
        for record in self:
            obj = record.profile
            if obj:
                if obj == "advancement" or obj == "liquidation_salary":
                    record.easy_movement = "yes"
                else:
                    record.easy_movement = "no"

                if obj == "advancement" or obj == "bank":
                    record.symbol = "subtraction"
                elif obj == "basic_salary" or obj == "liquidation_salary":
                    record.symbol = "sum"

    @api.multi
    def unlink(self):
        for rec in self:
            obj_self = self.env["easy.employee.cc"].search(
                [("easy_employe_cc_settlement_id", "=", self.id)]
            )
            if obj_self:
                raise ValidationError(
                    _(
                        "You can not delete a Settlement"
                        " maybe you want to archived"
                    )
                )
            return super(EasyEmployeeSettlement, self).unlink()

    @api.multi
    def open2archived(self):
        for rec in self:
            if rec.state == "open":
                rec.state = "archived"

    @api.multi
    def archived2open(self):
        for rec in self:
            if rec.state == "archived":
                rec.state = "open"

