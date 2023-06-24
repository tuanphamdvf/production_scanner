/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Layout } from "@web/views/layout";
import { KeepLast } from "@web/core/utils/concurrency";
import { Model, useModel } from "@web/views/helpers/model";
import { useService } from '@web/core/utils/hooks';
var session = require('web.session');

const { useRef, useState } = owl.hooks
const currentDate = new Date()
const currentMonth = currentDate.getMonth() + 1
const yearCurrent = currentDate.getFullYear()
const startOfMonth = new Date(yearCurrent, currentMonth - 1, 1); // Ngày đầu tháng
const endOfMonth = new Date(yearCurrent, currentMonth, 0); // Ngày cuối tháng

class VeryBasicModel extends Model {
    static services = ["orm"];

    constructor() {
        super(...arguments);

    }
    setup(params, { orm }) {
        this.model = params.resModel;
        this.orm = orm;
        this.keepLast = new KeepLast();
    }

    async load(params) {
        console.log(params, this.env)
        this.stafflist = await this.keepLast.add(
            this.orm.searchRead("hr.employee", params.domain, [])
        );

        // const currency_id = company_id.currency_id
        // this.currency_symbol = currency_id.symbol
        this.notify();
    }
}
VeryBasicModel.services = ["orm"];

class VeryBasicView extends owl.Component {

    state = {
        monthValue: "",
        staffValue: 0,
        numberDate: 0,
        lableChart1: [],
        listCustomer: [],
        month: currentMonth,
        startOfMonth: startOfMonth,
        endOfMonth: endOfMonth,
        year: yearCurrent

    };
    async setup() {
        this.ormService = useService('orm');
        this.model = useModel(VeryBasicModel, {
            resModel: this.props.resModel,
            domain: this.props.domain,
            orm: this.props.orm,

        });
        this.state = useState({
            monthValue: "",
            staffValue: 0,
            numberDate: 0,



        })

        this.render();
    }
    constructor() {
        super(...arguments);


    }
    async getData() {

        // this.listNewCustomer = await this.ormService.searchRead("res.partner", [['create_date', '>=', this.state.startOfMonth],
        // ['create_date', '<=', this.state.endOfMonth],]);



        this.render();
    }
    async addWorked(value, product, mrp) {
        console.log('workerd', value)
        await this.ormService.create("mrp.workorder", {
            'name': value.name,
            'production_id': mrp,
            'operation_id': value.id,
            'workcenter_id': value['workcenter_id'][0],
            'product_uom_id': product['uom_id'][0],
            // 'mrp_workorder_production_id': mrp
        })
    }

    async addProduction() {

        const stock_picking_type = await this.ormService.searchRead("stock.picking.type", [['active', '=', false], ['sequence_code', '=', 'PC']]);
        const productList = await this.ormService.searchRead("product.product", []);

        const product = productList[7]
        const bom = await this.ormService.searchRead("mrp.bom", [['product_id', '=', product.id]]);
        console.log('bom', productList)
        const routing = await this.ormService.searchRead("mrp.routing.workcenter", [['bom_id', '=', bom[0].id]]);
        // window.addEventListener('message', async (event) => {
        //     try {
        //         const value = JSON.parse(event.data)
        //         const { id, type } = value


        //         console.log(event)
        //     } catch {
        //         console.log("error")
        //     }
        //     console.log("thành công")
        //     window.ReactNativeWebView.postMessage("back");
        //     // Sử dụng dữ liệu nhận được từ React Native
        // });x
        console.log(stock_picking_type)
        const models = { "product_id": product.id, "product_seri": generateUUID(), "product_qty": 1, "product_uom_id": 1, "state": "confirmed", "bom_id": bom[0].id, 'reservation_state': "assigned" }
        console.log(routing)
        const mrp = await this.ormService.create("mrp.production", models);
        if (mrp && routing.length > 0) {
            routing.map((item) => {
                this.addWorked(item, product, mrp)
            })
        }
        console.log('mrp', mrp, product)

        const bom_line = await this.ormService.searchRead("mrp.bom.line", [['bom_id', '=', bom[0].id]]);
        console.log('bom', bom)
        if (bom.length > 0) {
            const vals = {
                "picking_type_id": stock_picking_type[0].id,
                'location_id': stock_picking_type[0].default_location_src_id[0],
                'location_dest_id': stock_picking_type[0].default_location_dest_id[0],
                'origin': mrp,

            }

            console.log('xong bom line', bom_line)
            const stockpickking = await this.ormService.create("stock.picking", vals);
            if (bom_line.length > 0) {
                bom_line.map(async (item) => {
                    const vals = {
                        'name': item['display_name'],
                        'product_id': item.product_id[0],
                        'product_uom_qty': item.product_qty,
                        'product_uom': item.product_uom_id[0],
                        'location_id': stock_picking_type[0].default_location_src_id[0],
                        'location_dest_id': stock_picking_type[0].default_location_dest_id[0],
                        'picking_id': stockpickking,
                        "raw_material_production_id": mrp,

                    }

                    const stockmove = await this.ormService.create("stock.move", vals);
                    const vals_Line = {
                        'product_id': item.product_id[0],
                        'product_uom_qty': item.product_qty,
                        'location_id': stock_picking_type[0].default_location_src_id[0],
                        'location_dest_id': stock_picking_type[0].default_location_dest_id[0],
                        'picking_id': stockpickking,
                        'product_uom_id': item.product_uom_id[0],
                        'move_id': stockmove,
                        'state': 'done'
                        // "qty_done": item.product_qty,

                    }
                    const stockmoveline = await this.ormService.create("stock.move.line", vals_Line);
                    console.log('sussec', stockmove)
                })

            }
        }
        return true

    }
    async finishProduction(seri) {
        const productionList = await this.ormService.searchRead("mrp.production", [['product_seri', '=', seri]]);

        if (productionList.length > 0) {
            const id = productionList[0].Id
            const models = { "state": "done" }
            const mrp = await this.ormService.write("mrp.production", id, models);
            console.log(mrp)
        } else {
            alert("not found production")
        }
    }
    async cancelProduction(seri) {
        const productionList = await this.ormService.searchRead("mrp.production", [['product_seri', '=', seri]]);

        if (productionList.length > 0) {
            const id = productionList[0].Id
            const models = { "state": "cancel" }
            const mrp = await this.ormService.write("mrp.production", id, models);
            console.log(mrp)
        } else {
            alert("not found production")
        }
    }
    async hanldeProduction(seri) {
        const productionList = await this.ormService.searchRead("mrp.production", [['product_seri', '=', "2491adfa-cbc0-4b7e-8bde-c27fc493e0fc"]]);
        console.log('production', productionList)
        const production = productionList[0]
        if (production.state == 'confirmed' || production.state == 'draft') {
            const models = { "state": "progress" }
            await this.ormService.write("mrp.production", production.id, models)
        }
        if (productionList.length > 0) {
            const id = productionList[0].id
            const listRouting = await this.ormService.searchRead('mrp.workorder', [['production_id', '=', id]])
            console.log(listRouting)
            if (listRouting.length > 0) {
                const progress = listRouting.find((i) => i.state == 'progress')
                if (isEmpty(progress)) {
                    console.log(progress.id)
                    const models = { "state": "done" }

                    await this.ormService.write("mrp.workorder", progress.id, models);

                    if (progress.operation_id == listRouting.length) {
                        console.log('finsih')
                        const models = { "state": "done" }
                        await this.ormService.write("mrp.production", id, models);
                        // await this.ormService.create("mrp.workorder", {
                        //     "state": 'done'
                        // })
                        // await this.ormService.write("mrp.production", id, models);
                    }

                } else {
                    const ready = listRouting.find((i) => i.state == 'ready')
                    if (isEmpty(ready)) {
                        const models = { state: "progress" }
                        await this.ormService.write("mrp.workorder", ready.id, models);
                    } else {
                        alert("Production order is not ready, please check the raw materials or status.")
                    }

                }
            }
            const models = { "state": "" }
            const mrp = await this.ormService.write("mrp.production", id, models);
            console.log(mrp)
        } else {
            alert("not found production")
        }
    }
    async mounted() {
        // const productionList = await this.ormService.searchRead("mrp.production", []);
        // console.log(productionList[productionList.length - 1])
        // this.addProduction()
    }

    onClick() {

        this.getData()
        this.render()
        console.log(this.ormService)

    }
    onStop() {
    }
    sendMessage(value) {
        // Gửi message tới ứng dụng React Native
        // window.ReactNativeWebView.postMessage(value);
    }

}

VeryBasicView.type = "barcode_view";
VeryBasicView.display_name = "VeryBasicView";
VeryBasicView.icon = "fa-heart";
VeryBasicView.multiRecord = true;
VeryBasicView.searchMenuTypes = ["filter", "favorite"];
VeryBasicView.components = { Layout };
VeryBasicView.template = "production_scanner.ChartTemplate";

registry.category("views").add("barcode_view", VeryBasicView);


