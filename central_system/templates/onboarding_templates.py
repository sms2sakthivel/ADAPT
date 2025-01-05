extract_onboarding_informations = {
  "system": "You are an intelligent assistant tasked to analyse and extract important details and dependencies of server/client in a larger solution. You always be correct and accurate in analysing and extracting requested informations.",
  "purpose": "Analyze the source code provided below and extract the requested details as mentioned in the 'instructions' and generate the json output as exactly mentioned in the example json output.",
  "instructions": [
    "Generate only the JSON Output exactly same as example_json_output. Do not include any other text or comments in the output.",
    "Extract the Exposed endpoints and capture them to the JSON Output.",
    "Extract the consumed endpoints and capture them to the JSON Output.",
    "Extract the bringup configurations such as port number, tls protocol, etc., and capture them to the JSON Output."
  ],
  "example_json_output": {
    "exposed_endpoints": [
      {
        "endpoint": "/",
        "methods": [
          {
            "method": "GET",
            "description": "Returns basic information about the User Service."
          }
        ]
      },
      {
        "endpoint": "/users",
        "methods": [
          {
            "method": "GET",
            "descriptions": "Retrieve a list of all users."
          },
          {
            "method": "POST",
            "descriptions": "Add a new user to the system."
          }
        ]
      },
      {
        "endpoint": "/users/{id}",
        "methods": [
          {
            "method": "GET",
            "descriptions": "Retrieve a user by their ID."
          },
          {
            "method": "PUT",
            "descriptions": "Modify details of an existing user."
          },
          {
            "method": "DELETE",
            "descriptions": "Remove a user by their ID."
          }
        ]
      },
      {
        "endpoint": "/swagger/*",
        "methods": [
          {
            "method": "GET",
            "description": "Serves the Swagger UI for API documentation."
          }
        ]
      }
    ],
    "consumed_endpoints": [
      {
        "endpoint": "/transaction/{id}",
        "methods": [
          {
            "method": "GET",
            "description": "Retrieve a transaction by their ID."
          }
        ],
        "port_config": "static",
        "port": 8005
      },
      {
        "endpoint": "/voucher/{id}",
        "method": [
          {
            "method": "GET",
            "description": "Retrieve a vocher by their ID."
          }
        ],
        "port_config": "dynamic",
        "port": 8006
      }
    ],
    "is_swagger_supported": True,
    "swagger_endpoint": "/swagger/*",
    "project_name": "User Management Service",
    "port": 8001,
    "communication_protocol": "HTTP",
    "is_tls_supported": False
  }
}