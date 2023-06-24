# -*- coding: utf-8 -*-
{
    'name': "Barcode Production Auto-Completion",
    "summary": "The module provides a barcode integration API for creating, initiating, commanding production, completing stages, pausing production commands, and searching for production commands, along with a mobile application.",
    'description': """The module provides a barcode integration API for creating, initiating, commanding production, completing stages, pausing production commands, and searching for production commands, along with a mobile application..
    """,
    "price": "399",
    "currency": "USD",
    'license': 'OPL-1',
    'author': "TTN SOFTWARE",
    'website': "TTNSOFTWARE.STORE",
    'category': 'App',
    'version': '15.2.2',
    'depends': ['base', 'mrp', "stock", 'hr'],

    'data': [
        'security/ir.model.access.csv',
        'views/owl_templates/owl_customer.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/stock_picking.xml',

        'views/casound_muahang.xml',

    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_qweb': [
            'production_scanner/static/src/xml/*',
            'production_scanner/static/src/xml/owl/*',
        ],
        'web.assets_backend': [
            'production_scanner/static/src/components/**/*',
            'production_scanner/static/src/scss/**/*',
            'production_scanner/static/lib/*',
            'production_scanner/static/src/js/**/*',
            'production_scanner/static/src/js/*',

        ],

    },

    'images': ['static/img/main_screenshot.gif']
}
