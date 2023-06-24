from odoo import models, fields, api, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    _description = 'Mrp Production '

    product_seri = fields.Char(string="Seri Number")
