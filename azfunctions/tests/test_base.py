import os
from pathlib import Path
from unittest import TestCase
from dotenv import load_dotenv

class BaseIntegrationTest(TestCase):
    @classmethod
    def setUpClass(cls):
        # Load test environment variables
        env_file = Path(__file__).parent / ".env.test"
        if not env_file.exists():
            raise FileNotFoundError(
                f"Test environment file not found at {env_file}. "
                "Please copy .env.test.example to .env.test and update the values as needed."
            )
        load_dotenv(env_file)

    def setUp(self):
        super().setUp()
        # Verify required environment variables
        self._verify_env_vars()

    def _verify_env_vars(self):
        required_vars = [
            "COSMOS_DB_URL",
            "COSMOS_DB_KEY",
            "COSMOS_DB_DATABASE",
            "AZURE_STORAGE_CONNECTION_STRING"
        ]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}. "
                "Please check your .env.test file."
            ) 