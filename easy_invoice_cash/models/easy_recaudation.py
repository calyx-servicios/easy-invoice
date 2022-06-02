from odoo import api, fields, models

class EasyRecaudation(models.Model):

    _inherit = "easy.recaudation"

    effective_journal = fields.Float('Effective Journal Amount', compute="_compute_moves")
    total_amount = fields.Float('Amount Box', compute="_compute_moves")
    journal_ids = fields.Many2many('account.journal', string='Journals')
    move_ids = fields.Many2many('account.move.line', string='Moves', compute="_compute_moves")
    report_date_from = fields.Date('From')
    report_date_to = fields.Date('To')

    @api.depends('journal_ids')
    def _compute_moves(self):
        total_amount = 0
        self.move_ids = False
        if self.journal_ids:
            for journal in self.journal_ids:
                aml = self.env['account.move.line'].search([('journal_id','=',journal.id),('account_id','=',journal.default_debit_account_id.id)])
                self.move_ids += aml
        if self.move_ids:       
            for move_id in self.move_ids:
                if move_id.balance:
                    total_amount += move_id.balance
        self.effective_journal = total_amount
        self.total_amount = total_amount + self.amount_box