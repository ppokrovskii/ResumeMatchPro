import azure.functions as func
from dotenv import load_dotenv
import os
import sys
import logging
import json

load_dotenv()

# add project root to sys.path
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

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

def handle_options(req: func.HttpRequest) -> func.HttpResponse:
    headers = get_cors_headers(req)
    if headers:
        return func.HttpResponse(status_code=204, headers=headers)
    return func.HttpResponse(status_code=400)

class CorsMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
        # Handle OPTIONS requests
        if req.method == "OPTIONS":
            return handle_options(req)

        # Process the request
        response = self.app(req, context)

        # Add CORS headers to response
        headers = get_cors_headers(req)
        if headers and hasattr(response, 'headers'):
            response.headers.update(headers)

        return response

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
app.middleware(CorsMiddleware)

# Import all function modules to register their blueprints
from file_upload.file_upload import file_upload_bp
from file_processing.file_processing import file_processing_bp
from matching.matching import matching_bp
from user_files.user_files import user_files_bp
from matching_results.matching_results import matching_results_bp
from users.users import users_bp

# Register all blueprints
app.register_blueprint(file_upload_bp)
app.register_blueprint(file_processing_bp)
app.register_blueprint(matching_bp)
app.register_blueprint(user_files_bp)
app.register_blueprint(matching_results_bp)
app.register_blueprint(users_bp)
