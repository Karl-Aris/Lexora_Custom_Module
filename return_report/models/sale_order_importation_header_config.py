from odoo import fields, api, models


class SaleOrderImportationHeader(models.Model):
    _name = "sale.order.importation.header.config"
    _description = "SO Importation Header Configuration"

    name = fields.Char()
    field_name = fields.Selection(selection=lambda self: self._compute_selection(), store=True)
    field_technical_name = fields.Char(compute="_compute_field_values")
    field_type = fields.Char(compute="_compute_field_values")

    relational_field = fields.Boolean(default=False)
    field_model = fields.Char(compute="_compute_field_values")
    child_field_id = fields.Many2one(
        'child.field.import',
        domain="""[
            ('res_model', '=', field_model),
            ('column_name', '=', name)
        ]""",
        store=True
    )
    is_required = fields.Boolean(default=False)

    def _compute_selection(self):
        so = self.env['sale.order']
        selections = [
            (field, so.fields_get()[field]['string'])
            for field in list(so.fields_get().keys())
        ]
        return sorted(selections, key=lambda i: i[1])

    @api.onchange('relational_field')
    def _onchange_relational_field(self):
        for rec in self:
            if rec.relational_field:
                model = self.env[rec.field_model]
                rec.child_field_id.search([
                    ("res_model", "=", model._name),
                    ("column_name", "=", rec.name)
                ]).unlink()
                selections = [
                    {
                        "name": model.fields_get()[field]['string'],
                        "column_name": rec.name,
                        "res_field": field,
                        "res_model": model._name,
                        "res_technical_field": rec.field_technical_name,
                    }
                    for field in list(model.fields_get().keys())

                ]
                selections = sorted(selections, key=lambda i: i['name'])
                rec.child_field_id.create(selections)
                rec.relational_field = True
            else:
                rec.child_field_id = None

    @api.depends("field_name")
    def _compute_field_values(self):
        so = self.env['sale.order']
        for rec in self:
            if rec.field_name:
                field_attrib = so.fields_get()[rec.field_name]
                field_type = field_attrib['type']
                field_name = rec.field_name
                field_model = ""

                if field_type in ['many2one', 'one2many', 'many2many']:
                    field_name = "%s|%s" % (field_name, field_type)
                    field_model = field_attrib['relation']
                elif field_type in ["date", "datetime"]:
                    field_name = "%s|%s" % (field_name, field_type)

                if rec.relational_field:
                    field_name = "%s:%s" % (field_name, rec.child_field_id.res_field)

                rec.field_type = field_type
                rec.field_technical_name = field_name
                rec.field_model = field_model
            else:
                rec.field_technical_name = ""
                rec.field_type = ""
                rec.field_model = ""



class ChildFieldImport(models.Model):
    _name = 'child.field.import'
    _description = "Child Field Import"

    name = fields.Char()
    res_model = fields.Char()
    res_field = fields.Char()
    res_technical_field = fields.Char()
    column_name = fields.Char()
    res_ids = fields.One2many(
        'sale.order.importation.header.config',
        'child_field_id',
    )