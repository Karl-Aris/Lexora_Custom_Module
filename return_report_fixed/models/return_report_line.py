from odoo import models, fields

class ReturnReportLine(models.Model):
    _name = 'return.report.line'
    _description = 'Return Report Line'

    report_id = fields.Many2one('return.report', string="Return Report", required=True, ondelete="cascade")
    product_id = fields.Many2one('product.product', string="Product", required=True)
    quantity = fields.Float(string="Quantity", default=1.0)
    reason = fields.Char(string="Reason for Return")
