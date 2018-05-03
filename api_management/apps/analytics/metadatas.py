from rest_framework.metadata import BaseMetadata


# pylint: disable=too-few-public-methods
class QueryMetadata(BaseMetadata):
    def determine_metadata(self, request, view):
        return {
            "swagger": "2.0",
            "info": {
                "description": "Endpoint analytics",
                "version": "1.0",
                "title": "Query Analytics",
            },
            "schemes": {
                0: "http"
            },
            "paths": {
                "/management/api/analytics/queries": {
                    "get": {
                        "summary": "Retorna las queries registradas",
                        "description": "Retorna paginadamente todas "
                                       "las queries registradas de todas las apis",
                        "consumes": {
                            0: "application/json",
                            1: "application/x-www-form-urlencoded",
                            2: "multipart/form-data",
                        },
                        "produces": {
                            0: "application/json",
                            1: "text/html",
                        },
                        "parameters": {
                            0: {
                                "name": "kong_api_id",
                                "in": "query",
                                "description": "filtra por id de api",
                                "required": False,
                                "type": "string",
                            },
                            1: {
                                "name": "from_date",
                                "in": "query",
                                "description": "filtra por fecha de query. "
                                               "Se obtienen todas las queries "
                                               "con fecha posterior a la indicada. YYYY-MM-DD",
                                "required": False,
                                "type": "string",
                            },
                            2: {
                                "name": "to_date",
                                "in": "query",
                                "description": "filtra por fecha de query. "
                                               "Se obtienen todas las queries "
                                               "con fecha anterior a la indicada. YYYY-MM-DD",
                                "required": False,
                                "type": "string",
                            },
                            3: {
                                "name": "limit",
                                "in": "query",
                                "description": "indica tamaño de pagina",
                                "required": False,
                                "type": "integer",
                            },
                            4: {
                                "name": "offset",
                                "in": "query",
                                "description": "indica desplazamiento de pagina",
                                "required": False,
                                "type": "integer",
                            },
                        },
                        "responses": {
                            200: {
                                "description": "operacion exitosa",
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "count": {
                                            "type": "integer",
                                        },
                                        "next": {
                                            "type": "url",
                                        },
                                        "previous": {
                                            "type": "url",
                                        },
                                        "results": {
                                            "type": "array",
                                            "items": {
                                                "$ref": "#/definitions/Query",
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            "definitions": {
                "Query": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer",
                        },
                        "ip_address": {
                            "type": "string",
                        },
                        "host": {
                            "type": "string",
                        },
                        "uri": {
                            "type": "string",
                        },
                        "api_data": {
                            "type": "integer",
                        },
                        "querystring": {
                            "type": "string",
                        },
                        "start_time": {
                            "type": "datetime",
                        },
                        "request_time": {
                            "type": "decimal",
                        },
                        "status_code": {
                            "type": "integer",
                        },
                        "user_agent": {
                            "type": "string",
                        }
                    },
                },
            },
        }
