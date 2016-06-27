require("../../node_modules/coren/shared/components/coren_backend")
require("../../node_modules/coren/shared/components/coren_test")

module.exports = {
    "basics": {
        "brand": "Coren",
        "title": "Coren :: Schema and REST",
        "description": "Simple site management",
        "css": [
            "/vendor/mocha.css",
            "/css/base.css"
        ],
        "javascript": [
            "/vendor/jquery.js",
            "/vendor/jquery-sortable.js",
            "/js/main.js"
        ],
        "apps": {
            "coren_backendAppView": "node_modules/coren/shared/components/coren_backend",
            "coren_testAppView": "node_modules/coren/shared/components/coren_test"
        },
        "rootUrl": "http://127.0.0.1",
        "port": 2160,
        "fonts": [
            "http://fonts.googleapis.com/css?family=Roboto:100,300,400,500"
        ],
        "socketPort": 2260,
        "socketUrl": "/sockets",
        "enableSockets": true,
        "testJavascript": [
            "/vendor/expect.js",
            "/vendor/mocha.js"
        ]
    },
    "coren": {
        "apiRoot": "/api",
        "loginUrl": "/login",
        "loginFailedUrl": "/login/failed",
        "loginRedirect": "/backend",
        "logoutUrl": "/logout",
        "failedUrl": "/login",
        "useBackend": true,
        "undo": true,
        "scripts": true,
        "authenticateURLs": false,
        "authenticateAPI": false,
        "dataTypes": {
            "checkbox": {
                "model": "checkboxFieldModel",
                "view": "checkboxFieldView",
                "editView": "checkboxEditView"
            },
            "count": {},
            "currency": {},
            "date": {},
            "dateTime": {},
            "duration": {},
            "entity": {},
            "entityType": {},
            "multiEntity": {},
            "multiEntityType": {},
            "float": {},
            "file": {},
            "id": {},
            "list": {},
            "number": {},
            "password": {},
            "percent": {},
            "pivot": {},
            "progress": {},
            "query": {},
            "json": {},
            "status": {},
            "text": {},
            "image": {},
            "orderedListSelection": {},
            "array": {}
        },
        "authenticate": false
    },
    "ui": {
        "doubleClickTimeout": 300,
        "clickThreshold": 10,
        "flickThreshold": 10,
        "defaultKeyNamespace": "app"
    }
}