import azure.functions as func
from dotenv import load_dotenv
import os
import sys
import logging

load_dotenv()

# add project root to sys.path
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

# Import all function modules to register their blueprints
from file_upload.file_upload import file_upload_bp
from file_processing.file_processing import file_processing_bp
from matching.matching import matching_bp
from user_files.user_files import user_files_bp
from matching_results.matching_results import matching_results_bp
from users.users import users_bp

# Create the app with explicit function names
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Register all blueprints with explicit function names
app.register_functions(file_upload_bp)
app.register_functions(file_processing_bp)
app.register_functions(matching_bp)
app.register_functions(user_files_bp)
app.register_functions(matching_results_bp)
app.register_functions(users_bp)
