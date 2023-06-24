# -*- coding: utf-8 -*-

from odoo import http
# -*- coding: utf-8 -*-
from odoo.http import request
from datetime import date

import json
from odoo.exceptions import UserError
import uuid


class ProductionApi(http.Controller):
    def call_button_mark_done(self, production_id):
        print(production_id)
        production = request.env['mrp.production'].browse(production_id)
        print(production)
        production.button_mark_done()

    @http.route('/web/session/authenticate', csrf=False, type='json', auth="none", methods=["POST"])
    def authenticate(self, db, login, password, base_location=None):
        print("hi")
        request.session.authenticate(db, login, password)
        print(request.env['ir.http'].session_info())
        return request.env['ir.http'].session_info()

    @http.route('/production/add', type='json', auth="user", method='POST')
    def list_production(self, **post):
        # danh_sach_production = request.env['mrp.production'].sudo().search([])
        current_day = date.today()
        user_id = request.uid
        name = post['name']
        productSeri = request.env["stock.production.lot"].search([('name', '=', name)])
        checkProduction = request.env["mrp.production"].search([('product_seri', '=', name)])
        if len(checkProduction) != 0:
            return {"status": 402, "message": "products have been manufactured  "}
        product = productSeri[0]['product_id']
        bom = []
        bom_id = False
        routing = []
        if len(product['bom_ids']) != 0:
            bom = product['bom_ids'][0]['bom_line_ids']
            bom_id = product['bom_ids'][0].id
            routing = product['bom_ids']['operation_ids']

        print('hi', product)
        productionenv = request.env['mrp.production']
        # stock_picking_type = self.env("stock.picking.type").search(
        #     [('active', '=', False), ('sequence_code', '=', 'PC')])
        # bom = request.env["mrp.bom"].search([('product_id', '=', product.id)])
        print(bom)
        # routing = request.env["mrp.routing.workcenter"].search(
        #     [('bom_id', '=', bom[0].id)])
        worked = []
        print(productionenv)
        onework = []

        if len(routing) != 0:
            for work in routing:
                print(work)
                val = {'time_ids': [], 'name': work['name'], 'workcenter_id': work['workcenter_id'].id,
                       'product_uom_id': 1,
                       'qty_producing': 0,
                       'duration_expected': work['time_cycle'], 'duration': work['time_cycle'],
                       'operation_id': work.id}
                onework.append(0)
                onework.append(uuid.uuid4().hex)
                onework.append(val)
                worked.append(onework)
                onework = []
        moves = []
        move = []
        print(moves, bom)
        # bom_line = request.env["mrp.bom.line"].search(
        #     [('bom_id', '=', bom[0].id)])
        if len(bom) != 0:
            for line in bom:
                print(line)
                print(uuid.uuid4())
                # Tạo một UUID tổng quát (version 4)
                vals = {'name': 'New', 'sequence': 1,
                        'company_id': 1,
                        'product_id': line['product_id'].id, 'product_uom_qty': line['product_qty'],
                        'product_uom': 1,
                        'location_id': 8, 'location_dest_id': 15, 'state': 'draft',
                        'price_unit': 0, 'group_id': False, 'propagate_cancel': False,
                        'move_line_ids': [], 'warehouse_id': 1, 'quantity_done': 0,
                        'additional': False, 'operation_id': False, 'bom_line_id': line.id}
                move.append(0)
                move.append(uuid.uuid4().hex)
                move.append(vals)
                moves.append(move)
                move = []
        print(moves)

        models = {'is_locked': True, "lot_producing_id": productSeri[0].id, 'product_seri': post['name'],
                  'priority': '0', 'product_id': product.id,
                  'product_description_variants': False, 'qty_producing': 0, 'product_qty': 1, 'product_uom_id': 1,
                  'bom_id': bom_id, 'date_planned_start': current_day, 'user_id': user_id,
                  'company_id': 1, 'move_finished_ids': [[0, uuid.uuid4().hex,
                                                          {'name': 'New', 'company_id': 1, 'product_id': product.id,
                                                           'product_uom_qty': 1, 'product_uom': 1, 'location_id': 15,
                                                           'location_dest_id': 8, 'move_dest_ids': [[6, False, []]],
                                                           'origin': 'New', 'group_id': False,
                                                           'propagate_cancel': False, 'warehouse_id': 1,
                                                           'operation_id': False, 'byproduct_id': False}]],
                  'move_raw_ids': moves,
                  'workorder_ids': worked,
                  'move_byproduct_ids': [], 'picking_type_id': 9, 'location_src_id': 8, 'location_dest_id': 8,
                  'origin': False, 'analytic_account_id': False, 'message_follower_ids': [], 'activity_ids': [],
                  'message_ids': []}

        # models = {"product_id": product.id, "product_seri": name(), "product_qty": 1, "product_uom_id": 1,
        #           "state": "confirmed", "bom_id": bom[0].id, 'reservation_state': "assigned", }
        print(models)
        productionenv._compute_product_uom_qty()
        productionenv._compute_show_lots()
        productionenv._compute_production_location()
        productionenv._onchange_product_id()
        productionenv._onchange_move_finished_product()
        productionenv._onchange_workorder_ids()

        production = productionenv.create(models)

        if production:
            production.action_confirm()
            return {"status": 200, "result": True, "message": "Susscess"}
        else:
            return {"status": 400, "result": False, "message": "Susscess"}

    @http.route('/production/handle', csrf=False, type='json', auth="user", method='POST')
    def handle_production(self, **post):
        current_day = date.today()
        name = post['name']
        productionenv = request.env['mrp.production']
        checkProduction = request.env["mrp.production"].search([('product_seri', '=', name)])
        if len(checkProduction) == 0:
            return {"status": False, "message": "Production order not yet created"}
        mrp = checkProduction[0]
        mrpenv = productionenv.browse(checkProduction[0].id)
        product = mrp.product_id
        routing = mrp.workorder_ids
        if len(routing) == 0:
            mrpenv.button_mark_done()
            result = mrp.write({
                'date_finished': current_day,
                'product_qty': 1,
                'qty_producing': 1,
                'priority': '0',
                'is_locked': True,
                'state': 'done',
            })
            stock_picking = request.env['stock.picking'].sudo().create({'picking_type_id': 7,
                                                                        'location_id': 8,
                                                                        'location_dest_id': 17,

                                                                        'move_lines': [(0, 0, {
                                                                            'product_id': product.id,
                                                                            'product_uom_qty': 1,
                                                                            'name': 'Incoming Shipment',
                                                                            'location_id': 8,
                                                                            'location_dest_id': 17,
                                                                            'product_uom': product.uom_id.id,
                                                                        })],
                                                                        })

            if stock_picking:
                return {"status": 200, "result": True, "messgae": "Susscess"}
            else:
                return {"status": 300, "result": False, "messgae": "Error"}
        else:
            for rout in routing:
                print(rout)
                if rout['state'] == 'ready' or rout['state'] == 'pending':
                    # models = {'state': "progress"}
                    # a = rout.write(models)
                    a = rout.button_start()
                    return {"status": 200, "result": True, "message": "Start Production", "models": a}
                elif rout['state'] == 'progress' and rout.id == routing[-1].id:
                    rout.button_finish()
                    # a = rout.write({'state': 'done'})
                    mrpenv.button_mark_done()
                    result = mrp.write({
                        'date_finished': current_day,
                        'product_qty': 1,
                        'qty_producing': 1,
                        'priority': '0',
                        'is_locked': True,
                        'state': 'done',
                    })
                    stock_picking = request.env['stock.picking'].sudo().create({'picking_type_id': 7,
                                                                                'location_id': 8,
                                                                                'location_dest_id': 17,

                                                                                'move_lines': [(0, 0, {
                                                                                    'product_id': product.id,
                                                                                    'product_uom_qty': 1,
                                                                                    'name': 'Incoming Shipment',
                                                                                    'location_id': 8,
                                                                                    'location_dest_id': 17,
                                                                                    'product_uom': product.uom_id.id,
                                                                                })],
                                                                                })

                    return {"status": 200, "result": True, "message": "Susscess production", "models": stock_picking}
                elif rout['state'] == 'progress':
                    # a = rout.write({'state': 'done'})
                    a = rout.button_finish()
                    return {"status": 200, "result": True, "message": "Susscess worked", 'models': a}

    @http.route('/production/pause', csrf=False, type='json', auth="user", method='POST')
    def pause_production(self, **post):
        current_day = date.today()
        name = post['name']
        productionenv = request.env['mrp.production']
        checkProduction = request.env["mrp.production"].search([('product_seri', '=', name)])
        if len(checkProduction) == 0:
            return {"status": False, "message": "Production order not yet created"}
        mrp = checkProduction[0]
        mrpenv = productionenv.browse(checkProduction[0].id)
        product = mrp.product_id
        routing = mrp.workorder_ids
        for rout in routing:
            print(rout)
            if rout['state'] == 'progress':
                a = rout.button_pending()
                return {"status": 200, "result": True, "message": "Pause Production", "models": a}
            else:
                return {"status": 200, "result": True, "message": "The production order is not being executed"}

    @http.route('/production/begin', csrf=False, type='json', auth="user", method='POST')
    def begin_production(self, **post):
        current_day = date.today()
        name = post['name']
        productionenv = request.env['mrp.production']
        checkProduction = request.env["mrp.production"].search([('product_seri', '=', name)])
        if len(checkProduction) == 0:
            return {"status": False, "message": "Production order not yet created"}
        mrp = checkProduction[0]
        mrpenv = productionenv.browse(checkProduction[0].id)
        product = mrp.product_id
        routing = mrp.workorder_ids
        for rout in routing:
            print(rout)
            if rout['state'] == 'progress':
                a = rout.button_start()
                return {"status": 200, "result": True, "message": "Start Production", "models": a}
            else:
                return {"status": 200, "result": True, "message": "The production order is not being executed"}

    @http.route('/production/cancel', csrf=False, type='json', auth="user", method='POST')
    def cancel_production(self, **post):

        current_day = date.today()
        name = post['name']
        productionenv = request.env['mrp.production']
        checkProduction = request.env["mrp.production"].search([('product_seri', '=', name)])
        if len(checkProduction) == 0:
            return {"status": False, "message": "Production order not yet created"}
        mrp = checkProduction[0]
        mrpenv = productionenv.browse(checkProduction[0].id)
        if mrpenv['state'] in ('confirmed', 'progress'):
            a = mrpenv.action_cancel()
            if a:
                return {"status": 200, "result": True, "message": "The production order is not being executed"}
            else:
                return {"status": 300, "result": False, "message": "Error"}
        else:
            return {"status": 400, "result": False, "message": "The production NOT progress or confirmed"}

    @http.route('/production/list', csrf=False, type='json', auth="user", method='POST')
    def list_production_user(self, **post):
        user = post['user']
        listproduct = []
        checkProduction = request.env["mrp.production"].search(
            [('state', 'in', ['progress', 'confirmed']), ('write_uid', '=', user)], order='write_date desc', limit=10)
        if checkProduction:
            work = ''
            w_state = ""
            for i in checkProduction:
                if len(i['workorder_ids']) != 0:
                    for w in i['workorder_ids']:
                        if w['state'] == 'progress':
                            work = w['name'],
                            w_state = w['state']
                            break
                        elif w['state'] in ('ready', 'pending'):
                            work = w['name'],
                            w_state = w['state']
                            break

                val = {
                    'id': i.id,
                    'name': i['name'],
                    'state': i['state'],
                    'product_name': i['product_id']['name'],
                    'work': work[0] if len(work) != 0 else '',
                    "w_state": w_state,
                    'product_seri': i['product_seri']

                }
                listproduct.append(val)
            return {"status": 200, "result": True, "message": "The production ",
                    "data": listproduct}

    @http.route('/production/find', csrf=False, type='json', auth="user", method='POST')
    def find_production(self, **post):
        name = post['name']
        checkProduction = request.env["mrp.production"].search([('product_seri', '=', name)])
        if len(checkProduction) != 0:

            mrp = checkProduction[0]
            if len(mrp['workorder_ids']) != 0 and mrp['state'] == 'progress':
                for m in mrp['workorder_ids']:
                    if m['state'] == 'progress':
                        return {"status": 200, "state": mrp['state'], "state_w": 'progress'}
                    if m['state'] in ('ready', 'pending'):
                        return {"status": 200, "state": mrp['state'], "state_w": 'ready'}
            elif mrp['state'] == 'progress':
                return {"status": 200, "state": mrp['state'], "state_w": 'none'}
            elif mrp['state'] == 'confirmed':
                return {"status": 200, "state": mrp['state']}
        else:
            return {"status": 300, "state": 'No Production'}

    @http.route('/production/scan', csrf=False, type='json', auth="user", method='POST')
    def scan_production(self, **post):
        name = post['name']
        checkProduction = request.env["mrp.production"].search([('product_seri', '=', name)])
        if len(checkProduction) != 0:
            works = []

            mrp = checkProduction[0]
            if len(mrp['workorder_ids']) != 0:
                for m in mrp['workorder_ids']:
                    vals = {
                        "name": m['name'],
                        "state": m['state']
                    }
                    works.append(vals)
            data = {
                'name': mrp['product_seri'],
                'product': mrp['product_id']['name'],
                'state': mrp['state'],
                'create_date': mrp['create_date'],
                'work': works
            }
            return {"status": 200, "data": data}
        else:
            return {"status": 300, }
