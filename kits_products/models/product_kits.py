from odoo import models, fields, api

class ProductKits(models.Model):
    _name = 'product.kits'
    _description = 'Product Kits'

    product_sku = fields.Char('Main Product SKU', required=True)
    product_id = fields.Many2one('product.product', compute='_compute_product_id', store=True, string='Sellable Product')

    name = fields.Char('Name', required=True)
    size = fields.Char('Size')
    collection = fields.Char('Collection')
    color = fields.Char('Color')

    cabinet_sku = fields.Char('Cabinet SKU')
    counter_top_sku = fields.Char('Counter Top SKU')
    faucet_sku = fields.Char('Faucet SKU')
    mirror_sku = fields.Char('Mirror SKU')
    product_image = fields.Image(
        string='Product Image',
        compute='_compute_product_image',
        store=True
    )
    image_1920 = fields.Image(string='Image', compute='_compute_image_1920', inverse='_inverse_image_1920', store=True)
    image_128 = fields.Image(string='Thumbnail', related='image_1920', store=True)

    # Product relations
    product_ids = fields.Many2many('product.product', compute='_compute_product_ids', string='Main Product Variants')
    cabinet_ids = fields.Many2many('product.product', compute='_compute_cabinet_ids', string='Cabinet Products')
    counter_top_ids = fields.Many2many('product.product', compute='_compute_counter_top_ids', string='Counter Top Products')
    faucet_ids = fields.Many2many('product.product', compute='_compute_faucet_ids', string='Faucet Products')
    mirror_ids = fields.Many2many('product.product', compute='_compute_mirror_ids', string='Mirror Products')

    _kit_images = fields.Binary(string="Kit Image Data")  # To store manual image input

    @api.depends('product_sku')
    def _compute_product_id(self):
        for kit in self:
            kit.product_id = self.env['product.product'].search([('default_code', '=', kit.product_sku)], limit=1) or False

    @api.depends('product_sku')
    def _compute_product_ids(self):
        for kit in self:
            if kit.product_sku:
                kit.product_ids = self.env['product.product'].search([('default_code', '=', kit.product_sku)])
            else:
                kit.product_ids = [(5, 0, 0)]

    @api.depends('cabinet_sku')
    def _compute_cabinet_ids(self):
        for kit in self:
            if kit.cabinet_sku:
                kit.cabinet_ids = self.env['product.product'].search([('default_code', '=', kit.cabinet_sku)])
            else:
                kit.cabinet_ids = [(5, 0, 0)]

    @api.depends('counter_top_sku')
    def _compute_counter_top_ids(self):
        for kit in self:
            if kit.counter_top_sku:
                kit.counter_top_ids = self.env['product.product'].search([('default_code', '=', kit.counter_top_sku)])
            else:
                kit.counter_top_ids = [(5, 0, 0)]

    @api.depends('faucet_sku')
    def _compute_faucet_ids(self):
        for kit in self:
            if kit.faucet_sku:
                kit.faucet_ids = self.env['product.product'].search([('default_code', '=', kit.faucet_sku)])
            else:
                kit.faucet_ids = [(5, 0, 0)]

    @api.depends('mirror_sku')
    def _compute_mirror_ids(self):
        for kit in self:
            if kit.mirror_sku:
                kit.mirror_ids = self.env['product.product'].search([('default_code', '=', kit.mirror_sku)])
            else:
                kit.mirror_ids = [(5, 0, 0)]

    @api.depends('_kit_images', 'product_id.image_1920')
    def _compute_image_1920(self):
        for kit in self:
            if kit._kit_images:
                kit.image_1920 = kit._kit_images
            elif kit.product_id and kit.product_id.image_1920:
                kit.image_1920 = kit.product_id.image_1920
            else:
                kit.image_1920 = False

    def _inverse_image_1920(self):
        for kit in self:
            kit._kit_images = kit.image_1920
    @api.depends('product_id.image_128', '_kit_images')
    def _compute_product_image(self):
        for kit in self:
            if kit._kit_images:
                kit.product_image = kit._kit_images
            elif kit.product_id and kit.product_id.image_128:
                kit.product_image = kit.product_id.image_128
            else:
                kit.product_image = False