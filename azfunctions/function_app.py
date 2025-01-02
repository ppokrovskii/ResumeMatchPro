import azure.functions as func
from dotenv import load_dotenv
import os
import sys

load_dotenv()

# add project root to sys.path
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

# Get allowed origins from environment variable
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
if not allowed_origins or allowed_origins[0] == "":
    # Default to localhost in development
    allowed_origins = ["http://localhost:3000"]

app = func.FunctionApp(
    http_auth_level=func.AuthLevel.ANONYMOUS,
    cors=allowed_origins,
    cors_credentials=True
)

# Import all function modules
from file_upload.file_upload import files_upload
from file_processing.file_processing import process_file
from matching.matching import match_resume
from user_files.user_files import get_user_files, delete_user_file
from matching_results.matching_results import get_matching_results
from auth_test import auth_test

# Register functions directly
app.register_functions(files_upload)
app.register_functions(process_file)
app.register_functions(match_resume)
app.register_functions(get_user_files)
app.register_functions(delete_user_file)
app.register_functions(get_matching_results)
app.register_functions(auth_test)
