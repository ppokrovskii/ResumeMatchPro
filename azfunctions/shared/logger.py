import logging
import os
import uuid
from typing import Optional

import azure.functions as func
from azure.monitor.opentelemetry import configure_azure_monitor

# Configure Azure Monitor only if we have the connection string
connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
if connection_string:
    configure_azure_monitor(
        connection_string=connection_string,
        disable_offline_storage=True,  # Ensure all telemetry is sent
        sampling_ratio=1.0,  # Sample 100% of telemetry
    )


def setup_logger(name: str = "resumematchpro") -> logging.Logger:
    """Initialize a logger with the given name."""
    logger = logging.getLogger(name)

    # Only set up the logger if it hasn't been configured yet
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(handler)

    return logger


def get_logger_with_context(
    request_id: Optional[str] = None, blueprint_name: Optional[str] = None
) -> logging.Logger:
    """Get a logger instance with optional request context and blueprint name."""
    # Use blueprint name if provided, otherwise use default
    logger_name = (
        f"resumematchpro.{blueprint_name}" if blueprint_name else "resumematchpro"
    )
    logger = setup_logger(logger_name)

    # Add request ID to log context if provided
    if request_id:
        extra = {"request_id": request_id}
        logger = logging.LoggerAdapter(logger, extra)

    return logger


def get_request_id(req: func.HttpRequest) -> str:
    """Extract or generate request ID for tracking."""
    return req.headers.get("x-ms-request-id") or str(uuid.uuid4())


# Create a singleton logger instance for application-wide logging
logger = setup_logger()
