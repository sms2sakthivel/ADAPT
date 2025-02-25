data = (
    {
        "path": "/users",
        "method": "GET",
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
                "schema": {"$ref": "#/definitions/model.UserResponse"},
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
                },
            },
        },
    },
)
