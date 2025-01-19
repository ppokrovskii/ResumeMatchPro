import azure.functions as func
from dotenv import load_dotenv
import os
import sys
import logging

load_dotenv()

# add project root to sys.path
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

# Get allowed origins from environment variable
# allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
# if not allowed_origins or allowed_origins[0] == "":
#     # Default to localhost in development
#     allowed_origins = ["http://localhost:3000"]

# app = func.FunctionApp(
#     http_auth_level=func.AuthLevel.ANONYMOUS,
#     cors=allowed_origins,
#     cors_credentials=True
# )

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Import all function modules to register their blueprints
from file_upload.file_upload import file_upload_bp
from file_processing.file_processing import file_processing_bp
from matching.matching import matching_bp
from user_files.user_files import user_files_bp
from matching_results.matching_results import matching_results_bp
from auth_test.auth_test import auth_test_bp
from user_files.models import UserFilesRequest, UserFilesResponse

# Register all blueprints
app.register_blueprint(file_upload_bp)
app.register_blueprint(file_processing_bp)
app.register_blueprint(matching_bp)
app.register_blueprint(user_files_bp)
app.register_blueprint(matching_results_bp)
app.register_blueprint(auth_test_bp)

# Register routes
@app.route(route="files", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_files(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('get_files function processed a request.')
    return user_files_bp.get_files(req)

@app.route(route="files/{file_id}", methods=["DELETE"], auth_level=func.AuthLevel.ANONYMOUS)
def delete_file(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Delete file function processed a request.')
    return user_files_bp.delete_file(req)
