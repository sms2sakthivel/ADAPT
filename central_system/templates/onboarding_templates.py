extract_onboarding_informations = {
    "system": "You are an intelligent assistant tasked to analyse and extract important details and dependencies of server/client in a larger solution. You always be correct and accurate in analysing and extracting requested informations.",
    "purpose": "Analyze the source code provided below and extract the requested details as mentioned in the 'instructions' and generate the json output as exactly mentioned in the example json output.",
    "instructions": [
        "Generate only the JSON Output exactly same as example_json_output. Do not include any other text or comments in the output.",
        "Extract the Exposed endpoints and capture them to the JSON Output.",
        "Extract the consumed endpoints and capture them to the JSON Output.",
        "Extract the bringup configurations such as port number, tls protocol, etc., and capture them to the JSON Output.",
    ],
    "example_json_output": {
        "exposed_endpoints": [
            {
                "endpoint": "/",
                "methods": [
                    {
                        "method": "GET",
                        "description": "Returns basic information about the User Service.",
                        "specification": {}
                    }
                ],
            },
            {
                "endpoint": "/users",
                "methods": [
                    {
                        "method": "GET",
                        "descriptions": "Retrieve a list of all users.",
                        "specification": {
                            "description": "Retrieve a list of all users",
                            "consumes": ["application/json"],
                            "produces": ["application/json"],
                            "tags": ["Users"],
                            "summary": "Get All Users",
                            "responses": {
                                "200": {
                                    "description": "OK",
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "$ref": "#/definitions/model.UserResponse"
                                        },
                                    },
                                },
                                "500": {
                                    "description": "Internal Server Error",
                                    "schema": {"$ref": "#/definitions/fiber.Error"},
                                },
                            },
                            "definitions": {
                                "fiber.Error": {
                                    "type": "object",
                                    "properties": {
                                        "code": {"type": "integer"},
                                        "message": {"type": "string"},
                                    },
                                },
                                "model.UserResponse": {
                                    "type": "object",
                                    "properties": {
                                        "email": {"type": "string"},
                                        "name": {"type": "string"},
                                        "user_id": {"type": "integer"},
                                        "user_name": {"type": "string"},
                                        "phone_number": {"type": "string"},
                                    },
                                },
                            },
                        },
                    },
                    {
                        "method": "POST",
                        "descriptions": "Add a new user to the system.",
                        "specification": {
                            "description": "Add a new user to the system",
                            "consumes": ["application/json"],
                            "produces": ["application/json"],
                            "tags": ["Users"],
                            "summary": "Create a New User",
                            "parameters": [
                                {
                                    "description": "User details",
                                    "name": "user",
                                    "in": "body",
                                    "required": True,
                                    "schema": {
                                        "$ref": "#/definitions/model.UserCreateRequest"
                                    },
                                }
                            ],
                            "responses": {
                                "201": {
                                    "description": "Created",
                                    "schema": {
                                        "$ref": "#/definitions/model.UserResponse"
                                    },
                                },
                                "400": {
                                    "description": "Bad Request",
                                    "schema": {"$ref": "#/definitions/fiber.Error"},
                                },
                                "500": {
                                    "description": "Internal Server Error",
                                    "schema": {"$ref": "#/definitions/fiber.Error"},
                                },
                            },
                            "definitions": {
                                "fiber.Error": {
                                    "type": "object",
                                    "properties": {
                                        "code": {"type": "integer"},
                                        "message": {"type": "string"},
                                    },
                                },
                                "model.UserCreateRequest": {
                                    "type": "object",
                                    "properties": {
                                        "email": {"type": "string"},
                                        "name": {"type": "string"},
                                        "password": {"type": "string"},
                                        "user_name": {"type": "string"},
                                        "phone_number": {"type": "string"},
                                    },
                                },
                                "model.UserResponse": {
                                    "type": "object",
                                    "properties": {
                                        "email": {"type": "string"},
                                        "name": {"type": "string"},
                                        "user_id": {"type": "integer"},
                                        "user_name": {"type": "string"},
                                        "phone_number": {"type": "string"},
                                    },
                                },
                            },
                        },
                    },
                ],
            },
            {
                "endpoint": "/users/{id}",
                "methods": [
                    {
                        "method": "GET",
                        "descriptions": "Retrieve a user by their ID.",
                        "specification": {
                            "description": "Retrieve a user by their ID",
                            "consumes": ["application/json"],
                            "produces": ["application/json"],
                            "tags": ["Users"],
                            "summary": "Get User by ID",
                            "parameters": [
                                {
                                    "type": "integer",
                                    "description": "User ID",
                                    "name": "id",
                                    "in": "path",
                                    "required": True,
                                }
                            ],
                            "responses": {
                                "200": {
                                    "description": "OK",
                                    "schema": {
                                        "$ref": "#/definitions/model.UserResponse"
                                    },
                                },
                                "404": {
                                    "description": "Not Found",
                                    "schema": {"$ref": "#/definitions/fiber.Error"},
                                },
                                "500": {
                                    "description": "Internal Server Error",
                                    "schema": {"$ref": "#/definitions/fiber.Error"},
                                },
                            },
                            "definitions": {
                                "fiber.Error": {
                                    "type": "object",
                                    "properties": {
                                        "code": {"type": "integer"},
                                        "message": {"type": "string"},
                                    },
                                },
                                "model.UserResponse": {
                                    "type": "object",
                                    "properties": {
                                        "email": {"type": "string"},
                                        "name": {"type": "string"},
                                        "user_id": {"type": "integer"},
                                        "user_name": {"type": "string"},
                                        "phone_number": {"type": "string"},
                                    },
                                },
                            },
                        },
                    },
                    {
                        "method": "PUT",
                        "descriptions": "Modify details of an existing user.",
                        "specification": {
                            "description": "Modify details of an existing user",
                            "consumes": ["application/json"],
                            "produces": ["application/json"],
                            "tags": ["Users"],
                            "summary": "Update an Existing User",
                            "parameters": [
                                {
                                    "type": "integer",
                                    "description": "User ID",
                                    "name": "id",
                                    "in": "path",
                                    "required": True,
                                },
                                {
                                    "description": "Updated user details",
                                    "name": "user",
                                    "in": "body",
                                    "required": True,
                                    "schema": {
                                        "$ref": "#/definitions/model.UserUpdateRequest"
                                    },
                                },
                            ],
                            "responses": {
                                "200": {
                                    "description": "OK",
                                    "schema": {
                                        "$ref": "#/definitions/model.UserResponse"
                                    },
                                },
                                "400": {
                                    "description": "Bad Request",
                                    "schema": {"$ref": "#/definitions/fiber.Error"},
                                },
                                "404": {
                                    "description": "Not Found",
                                    "schema": {"$ref": "#/definitions/fiber.Error"},
                                },
                                "500": {
                                    "description": "Internal Server Error",
                                    "schema": {"$ref": "#/definitions/fiber.Error"},
                                },
                            },
                            "definitions": {
                                "fiber.Error": {
                                    "type": "object",
                                    "properties": {
                                        "code": {"type": "integer"},
                                        "message": {"type": "string"},
                                    },
                                },
                                "model.UserResponse": {
                                    "type": "object",
                                    "properties": {
                                        "email": {"type": "string"},
                                        "name": {"type": "string"},
                                        "user_id": {"type": "integer"},
                                        "user_name": {"type": "string"},
                                        "phone_number": {"type": "string"},
                                    },
                                },
                                "model.UserUpdateRequest": {
                                    "type": "object",
                                    "properties": {
                                        "email": {"type": "string"},
                                        "name": {"type": "string"},
                                        "password": {"type": "string"},
                                        "user_id": {"type": "integer"},
                                        "user_name": {"type": "string"},
                                        "phone_number": {"type": "string"},
                                    },
                                },
                            },
                        },
                    },
                    {
                        "method": "DELETE",
                        "descriptions": "Remove a user by their ID.",
                        "specification": {
                            "description": "Remove a user by their ID",
                            "consumes": ["application/json"],
                            "produces": ["application/json"],
                            "tags": ["Users"],
                            "summary": "Delete a User",
                            "parameters": [
                                {
                                    "type": "integer",
                                    "description": "User ID",
                                    "name": "id",
                                    "in": "path",
                                    "required": True,
                                }
                            ],
                            "responses": {
                                "204": {"description": "No Content"},
                                "500": {
                                    "description": "Internal Server Error",
                                    "schema": {"$ref": "#/definitions/fiber.Error"},
                                },
                            },
                            "definitions": {
                                "fiber.Error": {
                                    "type": "object",
                                    "properties": {
                                        "code": {"type": "integer"},
                                        "message": {"type": "string"},
                                    },
                                },
                            }
                        },
                    },
                ],
            },
            {
                "endpoint": "/swagger/*",
                "methods": [
                    {
                        "method": "GET",
                        "description": "Serves the Swagger UI for API documentation.",
                    }
                ],
            },
        ],
        "consumed_endpoints": [
            {
                "endpoint": "/transaction/{id}",
                "methods": [
                    {
                        "method": "GET",
                        "description": "Retrieve a transaction by their ID.",
                    }
                ],
                "port_config": "static",
                "port": 8005,
            },
            {
                "endpoint": "/voucher/{id}",
                "method": [
                    {"method": "GET", "description": "Retrieve a vocher by their ID."}
                ],
                "port_config": "dynamic",
                "port": 8006,
            },
        ],
        "is_swagger_supported": True,
        "swagger_endpoint": "/swagger/*",
        "repository" : {
            "project_name": "User Management Service",
            "guid": "8913649E-4F41-44AC-B30C-92C43381A960",
            "description": "Creates and Manages the entire lifecycle of the users. It also provides Authentication & Authorization services for the users.",
            "jira_instance_url": "http://host.docker.internal:8080",
            "jira_project_key": "USERMAN",
        },
        "branch" : {
            "project_name": "User Management Service",
            "guid": "8913649E-4F41-44AC-B30C-92C43381A960",
            "description": "Creates and Manages the entire lifecycle of the users. It also provides Authentication & Authorization services for the users.",
            "jira_instance_url": "http://host.docker.internal:8080",
            "jira_project_key": "USERMAN",
        },
        "port": 8001,
        "communication_protocol": "HTTP",
        "is_tls_supported": False,
    },
}
