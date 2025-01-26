import os
import azure.functions as func

# Get allowed origins from environment variable
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
if not allowed_origins or allowed_origins[0] == "":
    # Default to localhost in development
    allowed_origins = ["http://localhost:3000"]

def get_cors_headers(req: func.HttpRequest) -> dict:
    origin = req.headers.get('Origin', '')
    if origin in allowed_origins:
        return {
            'Access-Control-Allow-Origin': origin,
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-MS-CLIENT-PRINCIPAL-CLAIMS',
            'Access-Control-Allow-Credentials': 'true'
        }
    return {}

def handle_cors(req: func.HttpRequest, response: func.HttpResponse) -> func.HttpResponse:
    """Add CORS headers to the response"""
    headers = get_cors_headers(req)
    if headers:
        for key, value in headers.items():
            response.headers[key] = value
    return response

def handle_options(req: func.HttpRequest) -> func.HttpResponse:
    """Handle OPTIONS requests"""
    headers = get_cors_headers(req)
    if headers:
        return func.HttpResponse(status_code=204, headers=headers)
    return func.HttpResponse(status_code=400) 