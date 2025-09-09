from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    qc_status_html = fields.Html(
        string="Quality Check Status",
        compute="_compute_qc_status_html",
    )

    @api.depends("x_quality_check.quality_state")
    def _compute_qc_status_html(self):
        for order in self:
            qc_html = ""
            for qc in order.x_quality_check:
                label = ""
                color = "secondary"

                if qc.quality_state == "pass":
                    label = "Good"
                    color = "success"  # green
                elif qc.quality_state == "fail":
                    label = "Damaged"
                    color = "danger"  # red
                else:
                    label = "Partial Return"
                    color = "warning"  # yellow/orange

                qc_html += (
                    f'<span class="badge rounded-pill text-bg-{color}">'
                    f"{label}</span><br/>"
                )

            order.qc_status_html = qc_html
