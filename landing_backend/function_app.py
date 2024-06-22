print("Function app started")
import logging
import azure.functions as func
from dotenv import load_dotenv
import sys

load_dotenv()

# logging.basicConfig(level=logging.DEBUG)
# logging.info("Function app started")

# add project root to sys.path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

from contact_details.contact_details import contact_details_bp

app.register_blueprint(contact_details_bp)