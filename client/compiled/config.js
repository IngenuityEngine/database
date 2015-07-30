require("../../node_modules/coren/shared/components/coren_backend")

module.exports = {
    "basics": {
        "brand": "Coren",
        "title": "Coren :: Schema and REST",
        "description": "Simple site management",
        "author": "Grant Miller",
        "css": [
            "/css/base.css"
        ],
        "javascript": [
            "/vendor/jquery.js",
            "/js/main.js"
        ],
        "apps": {
            "coren_backendAppView": "node_modules/coren/shared/components/coren_backend"
        },
        "port": 2150,
        "fonts": [
            "http://fonts.googleapis.com/css?family=Roboto:100,300,400,500"
        ]
    },
    "coren": {
        "apiRoot": "http://127.0.0.1:2160/api/",
        "useBackend": true,
        "undo": true,
        "scripts": true,
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
            "orderedListSelection": {}
        }
    }
}