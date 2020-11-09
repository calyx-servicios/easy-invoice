from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class WizardEasyEmployeeCcCreate(models.TransientModel):

    _name = "wizard.easy.employee.cc.create"
    _description = "Wizard Easy Employee C.C. Create"

    # Fields
    name = fields.Text(string="Description")
    amount = fields.Float(string="Amount",)
    date = fields.Date(string="Date", default=fields.Date.today)
    date_contable = fields.Date(
        string="Date Contable", default=fields.Date.today
    )
    partner_id = fields.Many2one("res.partner", string="Partner")
    employee_id = fields.Many2one("hr.employee", string="Employee")
    recaudation_id = fields.Many2one("easy.recaudation", string="Recaudation")
    easy_employe_cc_settlement_id = fields.Many2one(
        "easy.employe.cc.settlement", string="Tipo"
    )
    type = fields.Selection(
        [
            ("advancement", "Advancement"),
            ("bank", "Bank"),
            ("basic_salary", "Basic Salary"),
            ("liquidation_salary", "Liquidation Salary"),
        ],
        string="Type",
    )
    easy_movement = fields.Selection(
        [("yes", "Yes"), ("no", "No")],
        string="Easy Movement",
        related="easy_employe_cc_settlement_id.easy_movement",
    )
    # ends Field

    @api.onchange("easy_employe_cc_settlement_id")
    def _onchange_easy_employe_cc_settlement_id(self):
        for record in self:
            obj = record.easy_employe_cc_settlement_id
            if obj:
                record.type = obj.profile

    @api.multi
    def create_move(self):
        for self_obj in self:

            if (
                self_obj.easy_employe_cc_settlement_id.profile
                != "liquidation_salary"
                and self_obj.amount == 0.0
            ):
                raise ValidationError(
                    _("Can not create a Moviment with amount 0.00.")
                )
            return self.env["easy.employee.cc"].create_movement(
                self_obj.easy_employe_cc_settlement_id,
                self_obj.amount,
                self_obj.employee_id,
                self_obj.name,
                self_obj.recaudation_id,
                self_obj.date,
                self_obj.date_contable,
            )
