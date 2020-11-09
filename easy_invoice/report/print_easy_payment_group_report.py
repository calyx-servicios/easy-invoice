# -*- encoding: utf-8 -*-
################################################################################
#
#  This file is part of Aeroo Reports software - for license refer LICENSE file  
#
################################################################################


from odoo import api, models


class Parser(models.AbstractModel):
    _inherit = 'report.report_aeroo.abstract'

    _name = 'report.easy_payment_group'

        
    def _get_invoice(self, o):
        if o.group_type == 'in_group':
            lineas=[]
            for line_obj in o.in_invoice_ids:
                line = {
                    'nombre':line_obj.invoice_id.name,
                    'vencimiento': line_obj.invoice_id.date_expiration,
                    'residual': line_obj.residual_amount ,
                    'imputado': line_obj.amount2pay ,
                }
                lineas.append(line)  
            return lineas
        if o.group_type == 'out_group':
            lineas=[]
            for line_obj in o.out_invoice_ids:
                line = {
                    'nombre':line_obj.invoice_id.name,
                    'vencimiento': line_obj.invoice_id.date_expiration,
                    'residual': line_obj.residual_amount ,
                    'imputado': line_obj.amount2pay ,
                }
                lineas.append(line)  
            return lineas

   
    def _get_payments(self, o):
        lineas=[]
        if o.amount_money != 0.0:
            line = {
                'metodo':'Efectivo',
                'caja': o.recaudation_id.name,
                'monto': o.amount_money ,
            }
            lineas.append(line)  
        if o.partner_amount != 0.0:
            line = {
                'metodo':'Adelanto/Anticipo',
                'caja': '-',
                'monto': o.partner_amount ,
            }
            lineas.append(line)  
        if o.amount_total_rectificative != 0.0:
            line = {
                'metodo':'Monto en Rectificativas',
                'caja': '-',
                'monto': o.amount_total_rectificative ,
            }
            lineas.append(line)  


        return lineas


   
    def _get_total_payments(self, o):
        return o.amount_money +o.partner_amount+o.amount_total_rectificative

    def _get_total_residual(self, o):

        amount = 0.0
        for line in self._get_invoice(o):
            amount += line['residual']
        return amount

    @api.model
    def aeroo_report(self, docids, data):
        self = self.with_context(get_invoice=self._get_invoice)
        self = self.with_context(get_payments=self._get_payments)

        self = self.with_context(get_total_payments=self._get_total_payments)
        self = self.with_context(get_total_residual=self._get_total_residual)

        return super(Parser, self).aeroo_report(docids, data)

