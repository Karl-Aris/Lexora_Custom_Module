from odoo import api, fields, models, _


class PlatformGenericImport(models.Model):
    _name = "platform.generic"
    _description = "Platform Generic Importation"

    field_name = fields.Selection(
        selection=lambda self: self._compute_selection(),
        store=True,
        index=True,
    )
    field_type = fields.Char(compute="_compute_field_type")
    field_relation = fields.Char(compute="_compute_field_type")
    field_required = fields.Char(compute="_compute_field_type")
    platform_column_ids = fields.One2many('platform.generic.lines', 'field_id')

    def _compute_selection(self):
        so = self.env["sale.order"]
        selections = [
            (field, so.fields_get()[field]["string"])
            for field in list(so.fields_get().keys())
            if field not in ["order_line"]
        ]
        selections.append(("order_line_sku", "Order Line SKU"))
        selections.append(("order_line_amount", "Order Line Amount"))
        selections.append(("order_line_quantity", "Order Line Quantity"))
        selections.append(("order_line_desc", "Order Line Description"))

        return sorted(selections, key=lambda i: i[1])

    @api.depends("field_name")
    def _compute_display_name(self):
        so = self.env["sale.order"]
        for rec in self:
            try:
                rec.display_name = so.fields_get()[rec.field_name]['string']
            except KeyError:
                rec.display_name = rec.field_name.replace("_", " ").title()

    @api.depends("field_name")
    def _compute_field_type(self):
        so = self.env["sale.order"]
        for rec in self:
            if so.fields_get().get(rec.field_name):
                rec.write({
                    "field_type": so.fields_get()[rec.field_name].get("type"),
                    "field_relation": so.fields_get()[rec.field_name].get("relation"),
                    "field_required": so.fields_get()[rec.field_name].get("required"),
                })
            else:
                rec.write({
                    "field_type": "custom_field",
                    "field_relation": "custom_field",
                    "field_required": "custom_field",
                })


class PlatformGenericImportLine(models.Model):
    _name = "platform.generic.lines"
    _description = "Platform Generic Lines"

    name = fields.Char("Column", required=True)
    platform_id = fields.Many2one('platform.import', required=True)
    field_id = fields.Many2one('platform.generic', readonly=True)

    @api.depends("name", "platform_id")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s: %s" % (rec.platform_id.name, rec.name)


class PlatformImport(models.Model):
    _name = "platform.import"
    _description = "Platform Importation"
    _rec_name = "name"

    name = fields.Char()
    line_ids = fields.One2many('platform.generic.lines', 'platform_id')
