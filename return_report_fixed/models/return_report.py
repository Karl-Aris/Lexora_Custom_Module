from odoo import models, fields

class ReturnReport(models.Model):
    _name = "return.report"
    _description = "Return Report"

    name = fields.Char(string="Report Name", required=True)
    date = fields.Date(string="Date", default=fields.Date.today)
    customer_id = fields.Many2one("res.partner", string="Customer")
    product_id = fields.Many2one("product.product", string="Product")
    quantity = fields.Float(string="Quantity")
    reason = fields.Text(string="Reason for Return")
