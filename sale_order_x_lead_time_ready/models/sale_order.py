@api.depends('date_order')
def _compute_x_lead_time(self):
    StockPicking = self.env['stock.picking']
    for order in self:
        if not order.date_order:
            order.x_lead_time = 0
            continue

        pickings = StockPicking.search([
            ('sale_id', '=', order.id),
            ('state', '=', 'done')
        ])
        if not pickings:
            _logger = self.env['ir.logging']
            _logger.sudo().create({
                'name': 'Lead Time Debug',
                'type': 'server',
                'dbname': self._cr.dbname,
                'level': 'info',
                'message': f"No done pickings found for Sale Order {order.name}",
                'path': 'sale.order._compute_x_lead_time',
                'func': '_compute_x_lead_time',
                'line': '0',
            })
            order.x_lead_time = 0
            continue

        last_done = max(pickings.mapped('date_done'))
        order.x_lead_time = (last_done - order.date_order).total_seconds() / 86400.0  # float days
