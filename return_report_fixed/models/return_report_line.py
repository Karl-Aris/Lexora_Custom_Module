from odoo import models, fields


class ReturnReportLine(models.Model):
    _name = 'return.report.line'
    _description = 'Return Report Line'

    report_id = fields.Many2one(
        'return.report',
        string="Return Report",
        required=True,
        ondelete="cascade"
    )
    x_return_product = fields.Many2one(
        'product.template',
        string="Returned Product",
        required=True
    )
    quantity = fields.Float(
        string="Quantity",
        default=1.0
    )
    reason = fields.Char(
        string="Reason for Return"
    )
