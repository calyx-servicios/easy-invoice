# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
import openpyxl
import base64
from tempfile import TemporaryFile
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


class EasyEmployeeCcImport(models.Model):
    _description = "Employee Cc Import"
    _name = "easy.employee.cc.import"

    @api.onchange('settlement_id')
    def _onchange_settlement_id(self):
        for record in self:
            obj = record.settlement_id
            if obj:
                record.type = obj.profile

# Fields
    name = fields.Char(string='Reference/Description',)
    date = fields.Date(
        string='Date', default=lambda s: fields.Date.context_today(s))
    date_contable = fields.Date(string='Contable Date',
                                readonly=True,
                                states={'draft': [('readonly', False)]},
                                index=True,
                                help="Keep empty to use the current date",
                                copy=False)
    quantity = fields.Integer(string='Quantity',)
    import_file = fields.Binary('File')
    recaudation_id = fields.Many2one(
        'easy.recaudation', string='Recaudation Related')

    settlement_id = fields.Many2one(
        'easy.employe.cc.settlement',  string='Settlement')
    easy_movement = fields.Selection([('yes', 'Yes'),
                                      ('no', 'No')],
                                     string="Easy Movement", related='settlement_id.easy_movement')

    import_line_ids = fields.One2many(
        'easy.employee.cc.import.line', 'cc_import_id', string='Line Imported')
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirm'),
                              ('processed', 'Processed'),
                              ], string="State", default='draft')


# end Fields

    # #### Paginas para el uso de planillas de calculo en python
    # # http://ironsistem.com/tutoriales/python/modificar-documentos-de-excel-con-python/    (ESTA TIENE GRAFICOS)
    # # http://ironsistem.com/tutoriales/python/leer-documentos-de-excel-con-python/
    # # https://programacion.net/articulo/como_trabajar_con_archivos_excel_utilizando_python_1419
    # # https://stackoverflow.com/questions/43908296/how-read-excel-file-in-odoo-9/43909869
    @api.multi
    def draft2confirm(self):
        for rec in self:
            quantity = 0
            # esta linea es la que arche el Binary como archivo.
            file = base64.b64decode(rec.import_file)
            excel_fileobj = TemporaryFile('wb+')
            excel_fileobj.write(file)
            excel_fileobj.seek(0)
            # aca la combierte en hoja de calculo
            workbook = openpyxl.load_workbook(excel_fileobj, data_only=True)
            sheet = workbook[workbook.get_sheet_names()[0]]
            flag_first_line = True
            recaudation_id = None
            for line_tuplie in sheet.rows:
                if flag_first_line:
                    flag_first_line = False
                else:
                    self_ids = self.env['hr.employee'].search(
                        [('identification_id', '=', line_tuplie[0].value), ])
                    # Si encuentra 1 y solo 1 empleado con este identificador.
                    if len(self_ids) != 0:
                        amount2use = line_tuplie[1].value
                        employee_obj = self_ids[0]
                        vals = {
                            'name': 'Correcto: %s' % (line_tuplie[0].value),
                            'amount': amount2use,
                            'employee_id': employee_obj.id,
                            'cc_import_id': rec.id,
                        }
                        line_created = self.env[
                            'easy.employee.cc.import.line'].create(vals)
                        quantity += 1
                    else:  # error de cuando encuentre mas de uno o ninguno.
                        vals = {
                            'name': 'Error con Identificador: %s' % (line_tuplie[0].value),
                            'amount': line_tuplie[1].value,
                            'employee_id': None,
                            'cc_import_id': rec.id,
                        }
                        line_created = self.env[
                            'easy.employee.cc.import.line'].create(vals)
            rec.state = 'confirm'
            rec.quantity = quantity
        return True

    @api.multi
    def confirm2draft(self):
        for rec in self:
            for line in rec.import_line_ids:
                line.unlink()
        rec.state = 'draft'
        return True

    @api.multi
    def confirm2processed(self):
        for rec in self:
            for line in rec.import_line_ids:
                employee_cc_obj = self.env['easy.employee.cc'].create_movement(
                    rec.settlement_id, line.amount, line.employee_id,
                    rec.name, rec.recaudation_id, rec.date, rec.date_contable)
                # referencias cruzadas
                employee_cc_obj.import_line_id = line.id
                line.cc_line_id = employee_cc_obj.id
        rec.state = 'processed'
        return True

    @api.multi
    def unlink(self):
        for invoice in self:
            if invoice.state not in ('draft'):
                raise UserError(
                    _('You cannot delete an import which is not draft'))
            return super(EasyEmployeeCcImport, self).unlink()