from odoo import fields, api, models, _
from odoo.exceptions import ValidationError

class SaleOrderImportationTemplateData(models.Model):
    _name = "lexora.so.import.template.data"
    _description = "Data declared to templates used in sale order importation for seller platforms."
    
    name = fields.Char('Name', required=True)
    required = fields.Boolean("Required")
    
    @api.constrains('name')
    def _check_name(self):
        for rec in self:
            if rec.search([('name','=',rec.name),('id','!=',rec.id)]):
                raise ValidationError(_('Name must be unique!'))

class SaleOrderImportationTemplate(models.Model):
    _name = "lexora.so.import.template"
    _description = "Template declaration for sale order importation from selling platforms."
    
    name = fields.Char('Name', required=True)
    key = fields.Char('Key', required=True)
    mode = fields.Selection([('csv','CSV'),('xlsx','XLSX')],default = 'xlsx', string='Mode', required=True)
    data_row_start = fields.Integer('Data row start', default=1, help="The number of row where importable data begins.")
    
    template_data_ids = fields.One2many('lexora.so.import.template.data.sequence','template_id',string="Template data")
            
    
    
class SaleOrderImportationTemplateDataSequence(models.Model):
    _name = "lexora.so.import.template.data.sequence"
    _description = "Sequenced data  to templates used in sale order importation for seller platforms."
    _order = "sequence, id"
    
    data_id = fields.Many2one('lexora.so.import.template.data', string="Data", default = lambda self: self.env.ref('sale_order_import_lexora.lexora_sale_order_importation_template_data_pass_column'))
    sequence = fields.Integer('Sequence')
    template_id = fields.Many2one('lexora.so.import.template',string="Template")
    required = fields.Boolean(related='data_id.required')
    
    
    