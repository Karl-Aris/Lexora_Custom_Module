from odoo import models, fields, api, Command, _


class SaleOrderUploadResult(models.TransientModel):
    _name = "sale.order.upload.result"
    _description = "Sale Order Upload Result"
    _order = 'id desc'

    name = fields.Char()
    invalid_ids = fields.One2many('sale.order.invalid.data', 'upload_id')
    order_ids = fields.Many2many('sale.order')
    attachment = fields.Binary(string="File", required=True)


class SaleOrderInvalidData(models.TransientModel):
    _name = "sale.order.invalid.data"
    _description = "Sale Order Invalid Data"

    name = fields.Char(string="Row #")
    column = fields.Char()
    value = fields.Char()
    upload_id = fields.Many2one('sale.order.upload.result')
