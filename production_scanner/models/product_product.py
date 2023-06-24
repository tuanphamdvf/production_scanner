from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    serial_numbers = fields.One2many(
        'serial.number', 'product_id', string='Serial Numbers')
