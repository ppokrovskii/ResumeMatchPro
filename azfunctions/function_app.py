import logging
import os
import sys
from pathlib import Path

import azure.functions as func
from dotenv import load_dotenv
from shared.logger import setup_logging

load_dotenv()

# add project root to sys.path
sys.path.append(str(Path(__file__).parent))

# Initialize logging
setup_logging()

# Create the app with explicit function names
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Import all function modules to register their blueprints
from file_processing.file_processing import file_processing_bp
from file_upload.file_upload import file_upload_bp
from matching.matching import matching_bp
from matching_results.matching_results import matching_results_bp
from user_files.user_files import user_files_bp
from users.users import users_bp

# Register all blueprints with explicit function names
app.register_functions(file_upload_bp)
app.register_functions(file_processing_bp)
app.register_functions(matching_bp)
app.register_functions(user_files_bp)
app.register_functions(matching_results_bp)
app.register_functions(users_bp)

# Log application startup
logging.info("Function app initialized")
