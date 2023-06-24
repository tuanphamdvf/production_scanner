from odoo import models, fields, api, _
import qrcode
import base64
from io import BytesIO
from odoo.http import request
from odoo import exceptions, _


class MrpProductionLot(models.Model):
    _inherit = 'stock.production.lot'
    _description = 'stock.lot'

    qr_image = fields.Binary("QR Code", compute='_generate_qr_code')

    @api.depends('name')
    def _generate_qr_code(self):
        self.qr_image = generate_qr_code(self.name)


def generate_qr_code(value):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=20,
        border=4,
    )
    qr.add_data(value)
    qr.make(fit=True)
    img = qr.make_image()
    temp = BytesIO()
    img.save(temp, format="PNG")
    qr_img = base64.b64encode(temp.getvalue())
    return qr_img
