import azure.functions as func
from dotenv import load_dotenv
import sys

load_dotenv()

# add project root to sys.path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

from file_upload.file_upload import bp as file_upload_bp
from file_processing.file_processing import file_processing_bp
from matching.matching import matching_bp

app.register_blueprint(file_upload_bp)
app.register_blueprint(file_processing_bp)
app.register_blueprint(matching_bp)
