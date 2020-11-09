from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class EasyPaymentGroup(models.Model):

    _name = "easy.payment.group"
    _inherit = "easy.payment.group"

    @api.model
    def _default_recaudation_id(self):
        self_ids = self.env["easy.recaudation"].search([])
        for recaudation_obj in self_ids:
            for user_obj in recaudation_obj.user_ids:
                if user_obj.id == self.env.user.id:
                    return recaudation_obj.id
        return None

    recaudation_id = fields.Many2one(
        "easy.recaudation",
        string="Recaudation",
        ondelete="restrict",
        default=_default_recaudation_id,
    )
    payment_group_ids = fields.One2many(
        "easy.payment",
        "payment_group_id",
        string="Payment Line Created",
    )

    @api.multi
    def processed2cancel(self):
        for rec in self:
            # controlo que si hay plata para sacar de la recaudación
            if rec.group_type == "in_group":
                if (
                    not rec.recaudation_id.boolean_permit_amount_negative
                ):
                    if rec.recaudation_id.amount_box < rec.amount_money:
                        raise ValidationError(
                            _(
                                "You can not Cancel a Payment Group In without \
                                     Founds in Recaudation."
                            )
                        )
            # recorro las lineas, seteando estado a open y borro la linea
            for line_obj in rec.payment_group_ids:
                line_obj.invoice_id.state = "open"
                line_obj.unlink()
            # seteo en cancel el estado del grupo
            rec.state = "cancel"
            return rec

    @api.multi
    def prepared2processed(self):

        if not self.recaudation_id:
            raise ValidationError(
                _("You cant pay without a recaudation.")
            )
        # #### modo de "usar" el pago
        # 1) se usa el credito que tenga el aprtner para pagar las facturas
        #       se crean lineas de "uso" del credito
        #  (parecidos a la rectificativa q no poseen caja)
        # 2) las rectificativas que posea
        #       se crean lineas de "uso" con lineas de pagos relacionadas
        #  a la factura y la rectificativa
        # 3) el monto en pesos que va a pagar
        #       se crean lineas de pagos relacinadas a la caja
        name = ""
        sequence = self.recaudation_id.configuration_sequence_id
        if self.group_type == "out_group":
            # Usa los creditos/debitos para pagar las facturas descontando
            #  en la variable "amount2payed" de las lineas
            self._control_invoice_amount(self.out_invoice_ids)
            # Usa las rectificativas para pagar las facturas descontando
            #  en la variable "amount2payed" de las lineas
            self._use_rectificative_amount(
                self.out_invoice_ids, self.out_rectificative_ids
            )
            # Recorre las facturas controlando los estados y pagando
            #  lo que haya que pagar con efectivo
            for line_invoice_obj in self.out_invoice_ids:
                # controla si resta pagar algo en efectivo
                if line_invoice_obj.amount2payed > 0.0:
                    # genera la linea de pago en efectivo
                    payment_obj = line_invoice_obj.invoice_id.pay_out(
                        amount2pay=line_invoice_obj.amount2payed,
                        recaudation_obj=self.recaudation_id,
                        date=self.date,
                        payment_group_id=self.id,
                    )
                    if payment_obj:
                        payment_obj.payment_group_id = self.id
                # controla que el residual sea cero para
                #  terminar de pagar la factura
                if line_invoice_obj.invoice_id.residual_amount == 0.0:
                    line_invoice_obj.invoice_id.state = "paid"
            name = sequence.payment_group_sequence_out_id.next_by_id()

        if self.group_type == "in_group":
            # Usa los creditos/debitos para pagar las facturas
            # descontando en la variable "amount2payed" de las lineas
            self._control_invoice_amount(self.in_invoice_ids)
            # Usa las rectificativas para pagar las facturas
            # descontando en la variable "amount2payed" de las lineas
            self._use_rectificative_amount(
                self.in_invoice_ids, self.in_rectificative_ids
            )
            # Recorre las facturas controlando los estados y pagando
            # lo que haya que pagar con efectivo
            if not self.recaudation_id.boolean_permit_amount_negative:
                if self.recaudation_id.amount_box < self.amount_money:
                    raise ValidationError(
                        _(
                            "You can not Pay a debt without \
                                 Founds in Recaudation."
                        )
                    )
            for line_invoice_obj in self.in_invoice_ids:
                # controla si resta pagar algo en efectivo
                if line_invoice_obj.amount2payed > 0.0:
                    # genera la linea de pago en efectivo
                    payment_obj = line_invoice_obj.invoice_id.pay_in(
                        amount2pay=line_invoice_obj.amount2payed,
                        recaudation_obj=self.recaudation_id,
                        date=self.date,
                        payment_group_id=self.id,
                    )
                    if payment_obj:
                        payment_obj.payment_group_id = self.id
                # controla que el residual sea cero para
                #  terminar de pagar la factura
                if line_invoice_obj.invoice_id.residual_amount == 0.0:
                    line_invoice_obj.invoice_id.state = "paid"
            name = sequence.payment_group_sequence_in_id.next_by_id()

        self.state = "processed"
        if self.name == "Preparado":
            self.name = name
        return self

    @api.multi
    def _control_invoice_amount(self, invoice_ids):
        for line_invoice_obj in invoice_ids:
            if (
                line_invoice_obj.invoice_id.residual_amount
                != line_invoice_obj.residual_amount
            ):
                raise ValidationError(
                    _(
                        "No puede Procesar con Facturas que posean \
                            diferentes Montos Residuales a \
                                 los calculados.(Ref:%s)"
                        % str(line_invoice_obj.invoice_id.name)
                    )
                )
        return True

    @api.multi
    def _use_rectificative_amount(self, invoice_ids, rectificative_ids):

        sequence = self.recaudation_id.configuration_sequence_id
        sequence = sequence.refund_invoice_in_pay_sequence_id

        for rectificative_obj in rectificative_ids:
            if rectificative_obj.amount2pay == 0.0:
                continue
            else:
                amount_rectificative = rectificative_obj.amount2pay
                for line_invoice_obj in invoice_ids:
                    if rectificative_obj.amount2pay == 0.0:
                        break
                    if line_invoice_obj.amount2payed <= 0.0:
                        continue
                    else:
                        amount2pay = amount_rectificative
                        if amount2pay > line_invoice_obj.amount2payed:
                            amount2pay = line_invoice_obj.amount2payed
                        amount_rectificative -= amount2pay
                        rectificative_obj.amount2pay -= amount2pay
                        line_invoice_obj.amount2payed -= amount2pay

                        name = sequence.next_by_id()

                        if self.group_type == "in_group":

                            vals = {
                                "name": name,
                                "type": "pay_in",
                                "invoice_id": line_invoice_obj.invoice_id.id,
                                "amount_total": float(amount2pay)
                                * (-1.0),
                                "amount_in": amount2pay,
                                "date_pay": self.date,
                                "invoice_refund_id": (
                                    rectificative_obj.invoice_id.id
                                ),
                                "payment_group_id": self.id,
                            }
                            self.env["easy.payment"].create(vals)
                            vals2 = {
                                "name": name,
                                "type": "pay_out",
                                "invoice_id": rectificative_obj.invoice_id.id,
                                "amount_total": float(amount2pay),
                                "amount_out": amount2pay,
                                "date_pay": self.date,
                                "invoice_refund_id": (
                                    line_invoice_obj.invoice_id.id
                                ),
                                "payment_group_id": self.id,
                            }
                            self.env["easy.payment"].create(vals2)

                        if self.group_type == "out_group":
                            vals = {
                                "name": name,
                                "type": "pay_in",
                                "invoice_id": line_invoice_obj.invoice_id.id,
                                "amount_total": float(amount2pay),
                                "amount_out": amount2pay,
                                "date_pay": self.date,
                                "invoice_refund_id": (
                                    rectificative_obj.invoice_id.id
                                ),
                                "payment_group_id": self.id,
                            }
                            self.env["easy.payment"].create(vals)
                            vals2 = {
                                "name": name,
                                "type": "pay_out",
                                "invoice_id": rectificative_obj.invoice_id.id,
                                "amount_total": float(amount2pay)
                                * (-1.0),
                                "amount_in": amount2pay,
                                "date_pay": self.date,
                                "invoice_refund_id": (
                                    line_invoice_obj.invoice_id.id
                                ),
                                "payment_group_id": self.id,
                            }
                            self.env["easy.payment"].create(vals2)

            if rectificative_obj.invoice_id.residual_amount <= 0.0:
                rectificative_obj.invoice_id.state = "paid"
