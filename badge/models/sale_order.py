from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    order_line_qty_display_html = fields.Html(
        string="Ordered Products (HTML)",
        compute="_compute_order_line_qty_display_html",
    )

    order_line_qty_sku_html = fields.Html(
        string="Ordered SKUs (HTML)",
        compute="_compute_order_line_qty_display_html",
    )

    order_line_qty_display_text = fields.Char(
        string="Ordered Products (Text)",
        compute="_compute_order_line_qty_display_html",
    )

    order_line_qty_sku_text = fields.Char(
        string="Ordered SKUs (Text)",
        compute="_compute_order_line_qty_display_html",
    )

    order_line_qty_name_text = fields.Char(
        string="Ordered Product Names (Text)",
        compute="_compute_order_line_qty_display_html",
    )

    @api.depends("order_line")
    def _compute_order_line_qty_display_html(self):
        for order in self:
            html_combo = ""
            html_sku = ""
            plain = []
            skus = []
            names = []
            for line in order.order_line.filtered(
                lambda l: l.product_id.detailed_type == "product" and l.product_uom_qty > 0
            ):
                default_code = line.product_id.default_code or ""
                product_name = line.product_id.name or ""

                # COMBO: [SKU] Name badge
                html_combo += '<span class="badge rounded-pill text-bg-info"><strong>'
                if default_code:
                    html_combo += f"[{default_code}] "
                html_combo += f"{product_name}</strong></span>&nbsp;"
                html_combo += (
                    '<span class="badge rounded-pill text-bg-secondary"> Qty: '
                    + str(line.product_uom_qty)
                    + "</span><br/>"
                )

                # SKU-ONLY badge
                if default_code:
                    html_sku += (
                        '<span class="badge rounded-pill text-bg-info"><strong>'
                        + default_code
                        + "</strong></span>&nbsp;"
                        '<span class="badge rounded-pill text-bg-secondary"> Qty: '
                        + str(line.product_uom_qty)
                        + "</span><br/>"
                    )

                plain.append(
                    f"{product_name} (Qty: {line.product_uom_qty})"
                )
                if default_code:
                    skus.append(
                        f"{default_code} (Qty: {line.product_uom_qty})"
                    )
                if product_name:
                    names.append(
                        f"{product_name} (Qty: {line.product_uom_qty})"
                    )

            order.order_line_qty_display_html = html_combo
            order.order_line_qty_sku_html = html_sku
            order.order_line_qty_display_text = ", ".join(plain)
            order.order_line_qty_sku_text = ", ".join(skus)
            order.order_line_qty_name_text = ", ".join(names)
