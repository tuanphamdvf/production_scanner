from odoo import models, fields


class SerialNumber(models.Model):
    _name = 'serial.number'
    _description = 'Serial Numbers'

    seri = fields.Char(string='Serial Number', required=True)
    product_id = fields.Many2one(
        'product.product', string='Product', required=True)
